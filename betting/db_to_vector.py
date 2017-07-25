import sqlite3
import collections
import numpy as np

import tensorflow as tf

conn = sqlite3.connect('e0.db')
c = conn.cursor()
NUM_TEAMS = 21
NUM_MATCHES = 379

def get_number_of_teams():
    t = conn.cursor()
    t.execute("SELECT COUNT(*) FROM team")
    num_teams = t.fetchone()[0]
    return num_teams

def create_team_vector(team):
    max_size = get_number_of_teams()
    team_vector = np.zeros(max_size, np.int)
    # vector is 0 indexed
    team_vector[team-1] = 1
    return team_vector

def create_score_vector(home, away):
    return 1 if (home + away) > 2.5 else 0

def create_result_vector(home, away):
    result = np.zeros(3, np.int)

    if home > away: 
        result[0] = 1

    elif home == away:
        result[1] = 1

    else:
        result[2] = 1

    return result

def _int64_feature_vec(values):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=values))

def convert_to(writer, ht_v, at_v, ou25, er):

    example = tf.train.Example(features=tf.train.Features(feature={
        'home_team': _int64_feature_vec(ht_v),
        'away_team': _int64_feature_vec(at_v),
        'label_ou25': _int64_feature_vec([ou25]),
        'label_er': _int64_feature_vec(er)
        }))
    writer.write(example.SerializeToString())

def create_vector():
    home_team_index = 3
    away_team_index = 4
    home_goals = 5
    away_goals = 6

    filename = "train_data.tfrecords"
    filename_val = "val_data.tfrecords"
    print("Writing train + val")
    writer = tf.python_io.TFRecordWriter(filename)
    writer_val = tf.python_io.TFRecordWriter(filename_val)

    validation_count = 0
    validation_size = 60

    for row in c.execute("SELECT * FROM match ORDER BY RANDOM()"):
        home_team_vector = create_team_vector(row[home_team_index])
        away_team_vector = create_team_vector(row[away_team_index])
        over_under25 = create_score_vector(row[home_goals], row[away_goals])
        end_result = create_result_vector(row[home_goals], row[away_goals])
        if validation_count <= validation_size:
            convert_to(writer_val, home_team_vector, away_team_vector, over_under25, end_result)
        else: 
            convert_to(writer, home_team_vector, away_team_vector, over_under25, end_result)
        validation_count += 1

    writer.close()
    writer_val.close()

def main():
    create_vector()
    conn.close()

if __name__ == "__main__":
    main()