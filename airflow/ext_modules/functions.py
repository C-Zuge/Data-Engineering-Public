from sqlalchemy import null
import yaml
import pandas as pd
from yaml import CLoader as Loader
import os
import requests
import json
import logging
import ast
from sqlalchemy import create_engine
import pygsheets
from google.oauth2 import service_account
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, BlobServiceClient

log = logging.getLogger(__name__)

def loadFiles(filenames=[],rootPath=None):
    '''
    Read and Store every file given in filenames list, such as Feedz.yaml and db_config.yaml in a dictionary of dicts
    Feedz.yaml will be stored as Feedz and so on.
    '''
    if not rootPath:
        rootPath = os.path.dirname(os.path.realpath(__file__)) + os.sep
    filesContent = {}
    for filename in filenames:
        fileKey = filename.split('.')[0]
        with open(rootPath+filename,'r',encoding='ISO 8859-1') as f:
            filesContent[fileKey] = yaml.load(f,Loader=Loader)
    return filesContent

def connectSheet(service_account_info: str, sheetsUrl :str, **kwargs):
    SCOPES = ('https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive')
    if 'SCOPES' in kwargs.keys() and isinstance(tuple,kwargs['SCOPES']):
        SCOPES = kwargs['SCOPES']
    credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    gc = pygsheets.authorize(custom_credentials=credentials)
    doc = gc.open_by_url(sheetsUrl)
    return doc

def loadSheets(service_account_info: str, sheetsUrl :str,workSheet :str, clear=False, **kwargs) -> pd.DataFrame:
    doc = connectSheet(service_account_info,sheetsUrl, **kwargs)
    worksheet = doc.worksheet_by_title(workSheet)
    if 'end' in kwargs.keys():
        if 'start' in kwargs.keys():
            start_index = kwargs['start']
        else:
            start_index = 'A1'
        data = worksheet.get_values(start=start_index,end=kwargs['end'],include_tailing_empty_rows=False)
    else:     
        data = worksheet.get_all_values(include_tailing_empty_rows=False)
    if clear:
        workSheet.clear(fields='*')
    df = pd.DataFrame.from_records(data)
    df = df.rename(columns=df.iloc[0]).drop(df.index[0])
    return df

def connectPostgres(url, **kwargs):
    url_connection = None
    if not url:
        print("Exiting... url Connection failed due to credential errors")
        return None,None        
    elif url:
        url_connection = url
    elif kwargs:
        try:
            url_connection = f'postgresql://{kwargs["USER"]}:{kwargs["PASSWD"]}@{kwargs["HOST"]}:{kwargs["PORT"]}/{kwargs["DATABASE"]}'
        except:
            logging.error("Missing Parameters on Kwargs")
    
    engine = create_engine(url_connection)
    con = engine.connect()
    return engine, con

def load2db(df,name,schema,engine,con,mode='append'):
    if not df.empty:
        try:
            if mode in ['append','truncate']:
                con.execute(f'truncate table {schema}.{name}')
            if mode in ['insert','append']:
                df.to_sql(
                    name=name, 
                    con=engine, 
                    schema=schema, 
                    if_exists='append', 
                    index=False
                )
            logging.info(f'Loaded {name} Successfully!')
        except Exception as e:
            logging.info(f'Problem loading {name}! \n{e}')

def requestFeedz(linksAndToken):
    '''
    Given a set of feedz API Links into a dict, this function will request every single data from each link
    and store in a dict of Dataframes where the keys are the field and values a dataframe
    '''
    response = {}
    header = linksAndToken['Header']
    for field,link in linksAndToken['PrimaryLinks'].items():
        log.info(field,link)
        print(field,link)
        try:
            reply = requests.get(url=link,headers=header)
            reply.encoding = 'ISO-8859-1'
            reply = json.dumps(json.loads(reply.text)['data'])
            response[field] = pd.read_json(reply)
        except:
            log.exception('Failed to reach {} feedz section'.format(field))
    response = getSecundaryLinks(dictDf = response, linksAndToken=linksAndToken)
    return response

def getSecundaryLinks(dictDf,linksAndToken):
    '''
    TODO This function needs to interate over some table of Primary Links get the ids, 
    generate a url and treat the reponse for every request and store into a dataframe to import into database
    '''
    header = linksAndToken['Header']
    if linksAndToken['SecundaryLinks']:
        for field,link in linksAndToken['SecundaryLinks'].items():
            if field == 'consulta_celebracao':
                dictDf[field] = ConsultaCelebracao(dictDf,field,link,header)
            if field == 'resposta_super_pesquisa':
                dictDf[field] = respostaSuperPesquisa(dictDf,field,link,header)
    return dictDf

def requestMultiObjectReply(ids,link,header):
    dfList = []
    for id in ids:
        url = link.replace(":id",str(id))
        reply = requests.get(url,headers=header)
        reply.encoding = 'ISO-8859-1'
        if reply.text:
            reply = json.loads(reply.text)['data']
            [dfList.append(item) for item in reply]
    df = pd.read_json(json.dumps(dfList))
    return df

def connectBlobAzure(file_path,string_connection,container_name,blob_filepath):
    blob_connection = BlobServiceClient.from_connection_string(string_connection)
    blob_client = blob_connection.get_blob_client(container=container_name,blob=blob_filepath)
    with open(file_path, "rb") as blob_file:
        blob_client.upload_blob(data=blob_file)

def unpackDict(df, column, table, fillna=None):
    '''
    This function will extract the dict on the columns and transform in multiple columns on the root df.
    This function is very sensible regarding none/null values over the column.
    Params
        df is the entire dataframe.
        column is a single column that needs to be transformed.
    '''
    subDataframe = None
    columnContent = (d for idx, d in df[column].iteritems())
    try:
        if fillna is None:
            
            subDataframe = pd.DataFrame.from_dict(columnContent)
        else:
            subDataframe = pd.DataFrame.from_dict(columnContent).fillna(fillna)

        renameDf = {columnFragment: column.lower()+'_'+str(columnFragment).lower() for columnFragment in subDataframe.columns }
        subDataframe.rename(columns=renameDf,inplace=True)
        df = pd.concat([df,subDataframe],axis=1)
        df.drop(columns=[column],inplace=True)
    except:
        print('Error while unpacking {} dict from column {}'.format(table,column))
    return df

def unpackList(df):
    '''
    This function will extract the list brackets on the columns and extract each item to the column
    '''
    for column in df.columns:
        df[column] = df[column].apply(lambda col: str(str(col).replace('[','').replace(']','').replace("'","")))
    
    return df

def unpackColumns(df,table,fillna=null,save=False,encoding='UTF-8',sep=';',full=True):
    '''
    This function will apply both unpack funtions into the given dataframe to return a treated df
    If full parameter were True, the algorithm will run entirely, full mode.
    '''
    filterDict = df.apply(lambda col: col.astype(str).str.contains('^{|}$', regex=True).any(),axis=0)
    subDf = df.loc[: , filterDict].columns
    for column in subDf:
        df = unpackDict(df,column=column,table=table,fillna=fillna)
    
    if full:
        df = unpackList(df)

    if save:
        try:
            filename = os.sep.join([os.getcwd(),'{}.csv'.format(table)])
            df.to_csv(filename,sep=';',index=False,encoding=encoding)
        except:
            log.exception('Failed to save the {} table into a file! May be the encoding type'.format(table))

    return df

def treatUnpackColumns(df, columns):
    df = treatNoneInColumn(df,columns)
    df = treatUnpackDict(df,columns)

    return df

def treatNoneInColumn(df,columns):
    '''
    This function will replace all na (null/none) rows on the given column with the info of the other rows
    For this funtion works, the column rows need a dict format on the other rows. 
    '''
    for column in columns:
        filterData = df[column].notna()
        dataDf = df[filterData]

        content = dict(dataDf.iloc[[0]][column])
        key = list(content.keys())[0]
        keys = list(content[key].keys())
    
        if keys:
            params = {key: 'Not Found' for key in keys }

            values = {column: str(params)}
            df.fillna(value=values, inplace=True)
    return df

def treatUnpackDict(df, columns):
    '''
    This function was created for unpack and treat the dict right after the function treatNoneInColumn
    The function treatNoneInColumn returns a dict as a string and this can't be handled by other unpack functions
    This funciton will treat it and replace into the given dataframe returning also a df.
    '''
    for column in columns:
        columnContent = (d for idx, d in df[column].iteritems())

        listDict = []
        items = [*columnContent]
        for item in items:
            #Existem casos onde a linha está como string, advindo da função treatNoneInColumn
            if not isinstance(item,dict):
                dicionario = ast.literal_eval(item) # Transforms the str into dict object
                listDict.append(dicionario)
            else:
                listDict.append(item)
        subDataframe = pd.DataFrame.from_dict(listDict)
        renameDf = {columnFragment: column.lower()+'_'+str(columnFragment).lower() for columnFragment in subDataframe.columns }
        subDataframe.rename(columns=renameDf,inplace=True)
        df = pd.concat([df,subDataframe],axis=1)
        df.drop(columns=[column],inplace=True)    

    return df

def listDict2Dataframe(df,column):
    '''
    This function aims to transform a list of dictionaries related to one single line in another df that needs to be a new table
    This function will iterate over the list and dicts returning a sigle df with each son-dict as a row 
    '''
    columnContent = (d for idx, d in df[column].iteritems())
    items = [*columnContent]
    listDict=[]
    for item in items:
        for dicts in item:
            for dictionary in dicts:
                listDict.append(dictionary)
    resultFrame = pd.DataFrame.from_dict(listDict)
    return resultFrame

def null2empty(df):
    for column in df.columns:
        filter = df[column].astype(str).str.contains('<function null|nan|None',regex=True)
        nullPointers = pd.unique(df.loc[filter,column])
        df.replace(nullPointers, '' , inplace=True)
    return df

def changeEncoding(df,encoding='ISO-8859-1'):
    aux = df
    for column in df.columns:
        aux[column] = df[column].index.str.encode(encoding)
    return aux

'''
Examples of usage of Functions above this line
'''
def Colaboradores(df):
    df["cpf"].fillna(value=0,inplace=True)
    df = treatNoneInColumn(df,['direct_manager'])
    df = unpackColumns(df,table='Colaboradores',save=True)
    df["admission_at"] = pd.to_datetime(df["admission_at"])
    df["birth_at"] = pd.to_datetime(df["birth_at"])
    df["cpf"] = pd.to_numeric(df['cpf'],downcast='integer')
    df = null2empty(df)
    df.rename(columns={'employeeId':'employeeid'},inplace=True)
    return df

def Departamentos(df):
    df.drop_duplicates(subset=['id'],inplace=True)
    return df

def Celebracao(df):
    df.drop(columns=['comment'],inplace=True)
    df = unpackColumns(df,table='Celebracao')
    df['dt_create'] = pd.to_datetime(df["dt_create"])
    return df

def Enps(df):
    df = unpackColumns(df,table='Enps')
    df['dt_create'] = pd.to_datetime(df["dt_create"])
    df['deadline'] = pd.to_datetime(df["deadline"])
    df["detractors"] = pd.to_numeric(df['detractors'],downcast='integer')
    df["promoters"] = pd.to_numeric(df['promoters'],downcast='integer')
    df["passives"] = pd.to_numeric(df['passives'],downcast='integer')
    df["score"] = pd.to_numeric(df['score'],downcast='integer')
    df["status"] = pd.to_numeric(df['status'],downcast='integer')
    return df

def SuperPesquisa(df):
    df = unpackColumns(df,table='Super_Pesquisa')
    df = null2empty(df)
    return df

def respostaSuperPesquisa(dictDf,field,link,header):
    df = dictDf['super_pesquisa']
    df = requestMultiObjectReply(ids=df['id'],link=link,header=header)
    df = treatNoneInColumn(df,['profile'])
    df = treatUnpackDict(df, ['profile'])
    df = unpackColumns(df,table='Resp_SuperPesquisa')
    df = null2empty(df)
    df['id_profile_branch'] = pd.to_numeric(df['id_profile_branch'],downcast='integer')
    return df

def PesquisaRapida(df):
    df = unpackColumns(df,table='Pesquisa_Rapida')
    df['dt_created'] = pd.to_datetime(df["dt_created"])
    df['dt_deadline'] = pd.to_datetime(df["dt_deadline"])
    df = null2empty(df)
    return df

def NotificacoesEmpresa(df):
    df = unpackColumns(df,table='Notificacao_Empresa',save=False,full=False)
    df['dt_created'] = pd.to_datetime(df["dt_created"])
    return df

def ObjetivoV2(df):
    df = unpackColumns(df,table='Objetivo_v2',save=False,full=False)
    return df

def ObjetivoV3(df):
    df = treatNoneInColumn(df,['department','parent'])
    df = treatUnpackDict(df, ['department','parent'])
    df = unpackColumns(df,table='Objetivo_v3',save=False,full=False)
    df['dt_start'] = pd.to_datetime(df["dt_start"])
    df['dt_end'] = pd.to_datetime(df["dt_end"])
    key_result, checkinsDf = keyResultandCheckins(df,['key_results'])
    df['key_results'] = df['key_results'].astype(str)

    return df, key_result, checkinsDf

def keyResultandCheckins(df,column):
    keyResultDf = listDict2Dataframe(df,column)
    keyResultDf = unpackColumns(keyResultDf,table='Key_Results',save=False,full=False)
    checkins = keyResultDf.pop('checkins').to_frame()
    checkins = listDict2Dataframe(checkins,['checkins'])
    checkins = unpackColumns(checkins,table='Checkins',save=False,full=False)
    checkins['dt_create'] = pd.to_datetime(checkins["dt_create"])

    return keyResultDf, checkins  

def ConsultaCelebracao(dictDf,field,link,header):
    '''
    TODO This function aims to request all "ConsultaCelebração" on secundary link given a set o ids of "Celebração"
    '''
    field = field.split('_')[1]
    id = dictDf[field]['id'].to_list()
    id1 = id[0]
    link = link + str(id1)
    reply = requests.get(url=link,headers=header)
    reply.encoding = 'ISO-8859-1'
    reply = json.dumps(json.loads(reply.text)['data'])
