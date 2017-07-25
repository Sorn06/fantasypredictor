import sqlite3
import collections
import numpy as np

import tensorflow as tf

def get_num_records(tf_record_file):
    """
    Counts the number of records in tf_record_file
    """
    count = 0
    for _ in tf.python_io.tf_record_iterator(tf_record_file):
        count += 1
    return count

BATCH_SIZE = 10
DATA_FILE = 'train_data.tfrecords'
DATA_FILE_VAL = 'val_data.tfrecords'
BATCH_SIZE_VAL = get_num_records(DATA_FILE_VAL)
NUM_TEAMS = 21
DIM_EMB = 100

TRAIN_SIZE = get_num_records(DATA_FILE)

def parse_features(queue, batch_size, shuffle=False):
    reader = tf.TFRecordReader()
    _, serialized_example = reader.read(queue)
    if shuffle:
        batch = tf.train.shuffle_batch(
            [serialized_example],
            batch_size=batch_size,
            num_threads=2,
            capacity=1000 + 3 * batch_size,
            min_after_dequeue=1)

    else:
        batch = tf.train.batch([serialized_example], batch_size)

    features = tf.parse_example(
        batch,
        features={
            'home_team': tf.VarLenFeature(tf.int64),
            'away_team': tf.VarLenFeature(tf.int64),
            'label_ou25': tf.VarLenFeature(tf.int64),
            'label_er': tf.VarLenFeature(tf.int64)
        })

    return {
        'ht': features['home_team'],
        'at': features['away_team'],
        'label_ou25': features['label_ou25'],
        'label_er': features['label_er']
    }

def basic_model(x_ht, x_at, y_25, y_er):
    x = tf.concat([x_ht, x_at], axis=1)

    weight_emb = tf.get_variable(
        name='weight_emb',
        shape=[NUM_TEAMS*2, DIM_EMB],
        initializer=tf.contrib.layers.xavier_initializer()) 
    bias_emb = tf.get_variable(
        name='bias_emb', initializer=tf.constant(
            0.1, shape=[DIM_EMB]))
    weight_out = tf.get_variable(
        name='weight_out',
        shape=[DIM_EMB, 3],
        initializer=tf.contrib.layers.xavier_initializer()) 
    bias_out = tf.get_variable(
        name='bias_out', initializer=tf.constant(
            0.1, shape=[3]))

    net_emb = tf.matmul(x, weight_emb) + bias_emb
    emb = tf.nn.relu(net_emb)
    pred = tf.matmul(emb, weight_out) + bias_out

    cross_entropy = tf.reduce_mean(
      tf.nn.softmax_cross_entropy_with_logits(labels=y_er, logits=pred))

    optimizer = tf.train.AdamOptimizer().minimize(cross_entropy)

    return {
        'optimizer': optimizer,
        'x': x,
        'cost': cross_entropy,
        'y': y_er,
        'preds': tf.nn.softmax(pred)
        }

def queue_func(filename, batch_size, shuffle=False):
    queue = tf.train.string_input_producer([filename], shuffle=False)

    features = parse_features(queue=queue, batch_size=batch_size, shuffle=shuffle)

    print('File: {0} contains: {1} records'.format(filename, get_num_records(
        filename)))

    return tf.sparse_tensor_to_dense(features['ht']), tf.sparse_tensor_to_dense(features['at']), tf.sparse_tensor_to_dense(features['label_ou25']), tf.sparse_tensor_to_dense(features['label_er'])

def calculate_acc(preds, y):
    correct = 0
    incorrect = 0
    for p, y_ in zip(preds, y):
        if np.argmax(p) == np.argmax(y_):
            correct += 1
        else:
            incorrect += 1

    return correct, incorrect

def main():
    with tf.Session() as sess:
        x_ht_train, x_at_train, y_25_train, y_er_train = queue_func(DATA_FILE, BATCH_SIZE, True)
        x_ht_val, x_at_val, y_25_val, y_er_val = queue_func(DATA_FILE_VAL, BATCH_SIZE_VAL, False)

        graph_template = tf.make_template("", basic_model)

        graph_train = graph_template(
            x_ht=tf.cast(x_ht_train, tf.float32),
            x_at=tf.cast(x_at_train, tf.float32),
            y_25=tf.cast(y_25_train, tf.int32),
            y_er=tf.cast(y_er_train, tf.int32))

        graph_validation = graph_template(
            x_ht=tf.cast(x_ht_val, tf.float32),
            x_at=tf.cast(x_at_val, tf.float32),
            y_25=tf.cast(y_25_val, tf.int32),
            y_er=tf.cast(y_er_val, tf.int32))

        sess.run([tf.local_variables_initializer(),
                  tf.global_variables_initializer()])

        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(coord=coord, sess=sess)

        batch_count = 1
        epoch_count = 1
        lowest_val_cost = 1000
        train_cost = 0
        try:
            while not coord.should_stop():
                _, cost, x, y, preds = sess.run([graph_train['optimizer'],
                                            graph_train['x'],
                                            graph_train['cost'],
                                            graph_train['y'],
                                            graph_train['preds']])
                train_cost += cost
                """
                print("Cost:", cost)
                print("x:")
                print(x)
                print("y:")
                print(y)
                print("preds")
                print(preds)
                calculate_acc(preds, y)
                exit()
                print("\n\n\n")
                """

                if batch_count >= TRAIN_SIZE / BATCH_SIZE:
                    batch_count = 0

                    cost_val, y_val, preds_val = sess.run([graph_validation['cost'],
                                            graph_validation['y'],
                                            graph_validation['preds']])

                    correct, incorrect = calculate_acc(preds_val, y_val)
                    acc = correct / (correct + incorrect)
                    print("Acc:", acc)

                    if cost_val < lowest_val_cost: 
                        lowest_val_cost = cost_val
                        print("Cost:", cost_val)

                    print("EPOCH {0} DONE. Train cost avg: {1}".format(epoch_count, (train_cost/batch_count)))
                    train_cost = 0
                    epoch_count += 1

                batch_count += 1

        except tf.errors.OutOfRangeError:
            print('Done Loading')
        finally:

            coord.request_stop()

        print("Closing summary_writer")
        summary_writer.close()
        coord.join(threads=threads)

if __name__ == "__main__":
    main()