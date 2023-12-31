import os
import sys
import glob
import json
import datetime
from collections import Counter

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from nltk.corpus import stopwords

# Json data files importing
def get_json(path_channel):
    combined = []
    for json_file in glob.glob(f"{path_channel}*.json"):
        with open(json_file, 'r', encoding="utf8") as slack_data:
            data = json.load(slack_data)
            combined.append(data)

    return combined

def break_combined_weeks(combined_weeks):
    """
    Breaks combined weeks into separate weeks.
    
    Args:
        combined_weeks: list of tuples of weeks to combine
        
    Returns:
        tuple of lists of weeks to be treated as plus one and minus one
    """
    plus_one_week = []
    minus_one_week = []

    for week in combined_weeks:
        if week[0] < week[1]:
            plus_one_week.append(week[0])
            minus_one_week.append(week[1])
        else:
            minus_one_week.append(week[0])
            plus_one_week.append(week[1])

    return plus_one_week, minus_one_week

def get_msgs_df_info(df):
    msgs_count_dict = df.user.value_counts().to_dict()
    replies_count_dict = dict(Counter([u["user"] for r in df.replies if r != None for u in r]))
    mentions_count_dict = dict(Counter([u for m in df.mentions if m != None for u in m]))
    links_count_dict = df.groupby("user").link_count.sum().to_dict()
    return msgs_count_dict, replies_count_dict, mentions_count_dict, links_count_dict

def get_messages_dict(msgs):
    msg_list = {
            "msg_id":[],
            "text":[],
            "attachments":[],
            "user":[],
            "mentions":[],
            "emojis":[],
            "reactions":[],
            "thread_ts":[],
            "replies":[],
            "replies_to":[],
            "ts":[],
            "links":[],
            "link_count":[]
            }


    for msg in msgs:
        if "subtype" not in msg:
            try:
                msg_list["msg_id"].append(msg["client_msg_id"])
            except:
                msg_list["msg_id"].append(None)
            
            msg_list["text"].append(msg["text"])
            msg_list["user"].append(msg["user"])
            msg_list["ts"].append(msg["ts"])
            
            if "reactions" in msg:
                msg_list["reactions"].append(msg["reactions"])
            else:
                msg_list["reactions"].append(None)

            if "parent_user_id" in msg:
                msg_list["replies_to"].append(msg["ts"])
            else:
                msg_list["replies_to"].append(None)

            if "thread_ts" in msg and "reply_users" in msg:
                msg_list["replies"].append(msg["replies"])
                msg_list["thread_ts"].append(msg["thread_ts"])
            else:
                msg_list["replies"].append(None)
                msg_list["thread_ts"].append(None)
            
            # if "attachments" in msg :
            #     if msg["attachments"] != None:
            #         msg_list["attachments"].append(msg["attachments"])
            #     else : msg_list["attachments"].append(None)

            # else : msg_list["attachments"].append(None)

            if "attachments" in msg :
                msg_list["attachments"].append(msg["attachments"])
            else : msg_list["attachments"].append(None)
            
            if "blocks" in msg and msg["blocks"] != None:
                emoji_list = []
                mention_list = []
                link_count = 0
                links = []
                
                for blk in msg["blocks"]:
                    if "elements" in blk:
                        for elm in blk["elements"]:
                            if "elements" in elm:
                                for elm_ in elm["elements"]:
                                    
                                    if "type" in elm_:
                                        if elm_["type"] == "emoji":
                                            emoji_list.append(elm_["name"])

                                        if elm_["type"] == "user":
                                            mention_list.append(elm_["user_id"])
                                        
                                        if elm_["type"] == "link":
                                            link_count += 1
                                            links.append(elm_["url"])


                msg_list["emojis"].append(emoji_list)
                msg_list["mentions"].append(mention_list)
                msg_list["links"].append(links)
                msg_list["link_count"].append(link_count)
            else:
                msg_list["emojis"].append(None)
                msg_list["mentions"].append(None)
                msg_list["links"].append(None)
                msg_list["link_count"].append(0)
    
    return msg_list

def from_msg_get_replies(msg):
    replies = []
    if "thread_ts" in msg and "replies" in msg:
        replies = [u for r in msg["replies"] if r != None for u in r]
        # try:
            
        #     for ind in range(len(msg["replies"])):
        #         reply = msg["replies"][ind]
        #         if reply != None:
        #             for i in range(len(reply)):
        #                 reply[i]["thread_ts"] = msg["thread_ts"][ind]
        #                 reply[i]["message_id"] = msg["msg_id"][ind]
        #                 replies.append(reply[i])
        #         else: continue
        # except:
        #     pass
    return replies

def msgs_to_df(msgs):
    msg_list = get_messages_dict(msgs)
    df = pd.DataFrame(msg_list)
    return df

def process_msgs(msg):
    '''
    select important columns from the message
    '''

    keys = ["client_msg_id", "type", "text", "user", "ts", "team", 
            "thread_ts", "reply_count", "reply_users_count"]
    msg_list = {k:msg[k] for k in keys}
    rply_list = from_msg_get_replies(msg)

    return msg_list, rply_list

def get_messages_from_channel(channel_path):
    '''
    get all the messages from a channel        
    '''
    channel_json_files = os.listdir(channel_path)
    channel_msgs = [json.load(open(channel_path + f)) for f in channel_json_files]

    df = pd.concat([pd.DataFrame(get_messages_dict(msgs)) for msgs in channel_msgs])
    print(f"Number of messages in channel: {len(df)}")
    
    return df

def convert_2_timestamp(column, data):
    """convert from unix time to readable timestamp
        args: column: columns that needs to be converted to timestamp
                data: data that has the specified column
    """
    if column in data.columns.values:
        timestamp_ = []
        for time_unix in data[column]:
            if time_unix == 0:
                timestamp_.append(0)
            else:
                a = datetime.datetime.fromtimestamp(float(time_unix))
                timestamp_.append(a.strftime('%Y-%m-%d %H:%M:%S'))
        return timestamp_
    else: print(f"{column} not in data")
