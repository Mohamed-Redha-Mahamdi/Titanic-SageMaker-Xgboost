import boto3
import pandas as pd


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket = 'test-bucket-redha'
    file_key = 'raw/titanic.csv'

    # Télécharger le fichier depuis S3
    s3.download_file(bucket, file_key, '/tmp/titanic.csv')
    # Lire les données
    df = pd.read_csv('/tmp/titanic.csv')

    # pour avoir un apercu sur les noms, les types et les valuers manquantes des variables
    print(df.info())
    print(df.head())
    #supprimer des colonnes non nécessaires
    df = df.drop(['Ticket', 'PassengerId', 'Name'], axis=1)


    # Traitement des valeurs manquantes
    # Nous avons des valeurs manquantes dans Cabin et Age et Embarked
    # Pour Age et Embarked, nous allons faire un traitement, mais pour Cabin, nous allons la supprimer directement
    # Pour Embarked nous allons le convertir en catégorial puis remplacer les values manquantes par l'occurrence la plus répétée,
    # parce que il' ya juste un petit nombre de valeurs manquantes, tandis que pour Cabin c'est 70% et Cabin n'a pas beaucoup d'influence comparer aux autres
    frequent_category = df['Embarked'].mode().iloc[0]
    df['Embarked'] = df['Embarked'].fillna(frequent_category)

    def encode_embarked(dataframe):
        mapping = {'S': 0, 'Q': 1, 'C': 2}
        dataframe['Embarked'] = dataframe['Embarked'].replace(mapping)
        return dataframe

    df = encode_embarked(df)
    if 'Cabin' in df.columns:
        df = df.drop('Cabin', axis=1)

    df['Age'] = df['Age'].fillna(df['Age'].mean())
    # Encoder les variables catégorielles

    def encode_sex(dataframe):
        mapping = {'male': 1, 'female': 0}
        return dataframe['Sex'].replace(mapping)

    df['Sex'] = encode_sex(df)
    # Afficher quelques statistiques descriptives
    print(df.head())
    print(df.describe())
    
    # Écrire le DataFrame dans un fichier CSV
    df.to_csv('/tmp/processed_titanic.csv', index=False)

    # Télécharger le fichier dans le bucket S3
    s3.upload_file('/tmp/processed_titanic.csv', bucket, 'processed/processed_titanic.csv')


    return {'statusCode': 200, 'body': 'Data processing completed'}
