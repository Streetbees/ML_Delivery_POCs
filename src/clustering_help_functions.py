import pandas as pd
import numpy as np
from ml_clustering.dataset import DataSet
from ml_clustering.clustering import Clustering

def define_type_of_editing(cluster_modif:dict, cluster_names:dict, clustering:Clustering):
    '''

    Parameters
    ----------
    cluster_modif: it is a dictionary with the format {"location_name" : list, "question_name" : nested_list,
    "question_values" : list, "from_cluster" : int, "to_cluster" : int, "cluster_name" : str},
    cluster_names: dictionary with the mappings between cluster id and cluster name
    clustering: the clustering object

    Returns
    -------

    '''
    if (cluster_modif['to_cluster'] is None) & (cluster_modif['cluster_name'] is not None) & (cluster_modif['question_name'] is None):
        print("Cluster renaming...")
        cluster_names[cluster_modif['from_cluster']] = cluster_modif['cluster_name']
    else:
        if (cluster_modif['to_cluster'] == clustering.nclusters()):
            print("Creating new cluster...")
            cluster_names[cluster_modif['to_cluster']] = cluster_modif['cluster_name']
        if (cluster_modif['question_name'] is None):
            print("No filter applied to this modification...")
    if (cluster_modif['to_cluster'] > clustering.nclusters()):
        print("Error! The cluster number you assigned is out of scale")
    return cluster_modif, cluster_names

def format_clustering_modification_dictionary(mod:dict):
    '''

    Parameters
    ----------
    mod: it is the modification coming from the json file
    Returns a dictionary in the right format as it should be used in the editor.select()
    -------

    '''
    d = dict()
    d['location_name'] = mod['location_name']
    try:
        dict(zip(mod['question_name'], mod['question_values']))
    except:
        pass
    else:
        d = {**d, **dict(zip(mod['question_name'], mod['question_values']))}

    # If the dictionary is empty assign to it the None value
    if len(d) == 0:
        print("Empty dictionary")
        d = None
    return d

def create_clustering_object(input_df:pd.DataFrame, labels_column:str, iv:list, id_column:str):
    '''

    Parameters
    ----------
    input_df: pandas dataframe with the features and the cluster_ids
    labels_column: clsuter_id
    iv: the independent variables of clustering
    id_column: usually 'id' or 'submission_id'

    Returns
    -------
    Returns the clustering object of a dataframe that has  clusterPids

    '''
    l = np.array(input_df[labels_column].tolist())
    input_df_DataSet = DataSet(input_df)
    encoded = input_df_DataSet.encode_features(features=iv, ids=id_column)
    clustering = Clustering(encoded, l)
    return clustering

def create_mapping_df(clustering:Clustering, cluster_names_dict:dict, cluster_cols_names:dict):
    '''

    Parameters
    ----------
    clustering: clustering Object
    cluster_names_dict: dictionary with the cluster name of each cluster id
    cluster_cols_names : dictionary to rename 'cluster_id' and 'cluster_name' if is needed

    Returns the submission ids with the cluster id and cluster name of each one of it
    -------

    '''
    mapping_df = pd.DataFrame(list(zip(clustering.submission_mapping()['id'], clustering.submission_mapping()['cluster_id'])), columns =['id', 'cluster_id'])
    mapping_df['cluster_name'] = mapping_df['cluster_id'].apply(lambda x: cluster_names_dict[x])
    try:
        mapping_df.rename(columns=cluster_cols_names, inplace=True)
    except:
        pass
    return mapping_df

def append_clusters_to_dataframe(input_df:pd.DataFrame, clustering:Clustering, cluster_names_dict, cluster_name:str, id_col:str='submission_id'):
    '''

    Parameters
    ----------
    input_df: dataframe with the data
    clustering: clustering object with all the modifications
    cluster_names_dict: dictionary mapping cluster ids to cluster names
    cluster_name: the name of the clustering column

    Returns
    -------
    Return the initial dataframe with 2 additional columns, the cluster name and the corresponding number. If columns with the same name exist, they get removed
    '''
    # Build mapping dataframe
    mapping_df = create_mapping_df(clustering, cluster_names_dict, {'cluster_id':  f"{cluster_name}_number",
                                                                    'cluster_name': f"{cluster_name}_name"})

    # Check that the columns do not exist  -- If it exists, replace them with the ones coming from mapping_df
    clusters_list = [f"{cluster_name}_number", f"{cluster_name}_name"]
    for col in clusters_list:
        if col in input_df.columns:
            input_df.drop([col], axis=1, inplace=True)
            print(f"Column {col} was deleted")

    input_df_extended = input_df.merge(mapping_df, left_on=id_col, right_on="id").drop(['id'], axis=1)  # by default it is called 'id' in the mapping_df
    print(input_df_extended.shape)
    return input_df_extended