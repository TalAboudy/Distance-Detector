import pandas as pd
import numpy as np
import math
import datetime
import sys


w = 1.00  # car width
l = 2.00  # car length
t = 2  # the time related to the distance requiered to keep from the car in front. In this specific case- 2 seconds


# get input files from cmd
if len (sys.argv) != 3 :
    print ("Error: Wrong input")
    sys.exit (1)

path=sys.argv[0]
car_data=sys.argv[1]
all_cars_data=sys.argv[2]

df_car = pd.read_csv(car_data, delimiter=',')
df_all_cars = pd.read_csv(all_cars_data, delimiter=',')


# Given 2 coordinates representing the ride vector, return the angel between the vector and x axis
def calculate_angel(x1, x2, y1, y2):
    if (x2==x1): # avoid dividing by 0
        return 0.5*math.pi if y2>=y1 else 1.5*math.pi
    angel = (np.arctan((y2 - y1) / (x2 - x1)))
    return angel if angel > 0 else (angel + math.pi)  # the angel in rad

# Calculate the distance between 2 coordinates
def calc_distance(x1, x2, y1, y2):
    return (math.sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2)))


df_car['time'] = pd.to_datetime(df_car['time'])
df_all_cars['time'] = pd.to_datetime(df_all_cars['time'])
df_car['alert'] = 0

for i in range(df_car.shape[0]):
    x1 = df_car.at[i, 'x']  # current x coordinate
    y1 = df_car.at[i, 'y']  # current y coordinate


    if (df_car.at[i, 'time'] + datetime.timedelta(0, t)) <= max(df_car['time']):  # for records before the last two seconds of the ride
        x2 = max(df_car[df_car['time'] == df_car.at[i, 'time'] + datetime.timedelta(0, t)]['x'])  # x coordinate after 2 sec
        y2 = max(df_car[df_car['time'] == df_car.at[i, 'time'] + datetime.timedelta(0, t)]['y'])  # y coordinate after 2 sec

        distance = calc_distance(x1, x2, y1, y2)  # calculate the distance the car passed in the next 2 sec
        alph = calculate_angel(x1, x2, y1, y2)  # the agnel between the ride vector in these 2 sec and the x axis

    else:  # for records in the last two seconds of the ride
        distance = df_car.at[i, 'v']*10/36*2  # calculate the distance the car will pass in the next 2 sec (v is given in km/h)
        alph = calculate_angel(0, df_car.at[i, 'direction_x'], 0, df_car.at[i, 'direction_y'])  # the agnel between the direction vector and the x axis


    mini_df = df_all_cars[df_all_cars['time'] == df_car.at[i, 'time']]  # mini df of the cars records with the same timestemp
    mini_df['rotated_x'] = np.cos(alph) * (mini_df['x'] - x1) + np.sin(alph) * (mini_df['y'] - y1)  # rotate eache car location to coordinate system in which the ride vector is on the x axis
    mini_df['rotated_y'] = np.cos(alph) * (mini_df['y'] - y1) - np.sin(alph) * (mini_df['x'] - x1)
    mini_df['is_in_area'] = ((mini_df['rotated_x'] >= 0) & (mini_df['rotated_x'] <= (distance + l)) & (mini_df['rotated_y'] >= (-w / 2)) & (mini_df['rotated_y'] <= (w / 2)))# check per car if it was in the '2 seconds area'

    df_car.at[i, 'alert'] = mini_df['is_in_area'].any(axis=0) * 1 # alert if at least one car was in '2 seconds area'

df_car.to_csv(path_or_buf=path+'_w_alerts.csv', sep=',',index=False)  # save the car dataset with the adittional 'alert' column



