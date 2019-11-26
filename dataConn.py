
import psycopg2
import pandas as pd


def str_bin_to_int(str_bin):
    
    ''' Change string binary into int binary '''
    
    if str_bin == 'bad':
        int_bin = 0
    else:
        int_bin = 1
    return(int_bin)



# load data, assuming RAM capacity is enough and file is in current directory
my_data = pd.read_csv("data.tsv", sep="\t")


def populate():
    try:
        conn=psycopg2.connect("dbname='dbtoy' user='postgres' host='localhost' password='test'")
    except:
        print("I am unable to connect to the database.")


    if (conn):
        cursor = conn.cursor()
        insert_query_sample = """INSERT INTO sample(sample_num, dim_1, dim_2, dim_3, dim_4, dim_5) VALUES (%s,%s,%s,%s,%s,%s)"""
        insert_query_label = """INSERT INTO label(sample_num, sample_type, sample_type_binary) VALUES (%s,%s,%s)"""
        for i,row in my_data.iterrows():
            try:
                query_data_s = tuple([row['sample'][7::], row['dim 1'], row['dim 2'], row['dim 3'], row['dim 4'], row['dim 5']])
                cursor.execute(insert_query_sample, query_data_s)
                query_data_l = tuple([row['sample'][7::], row['sample_type'][5::], str_bin_to_int(row['sample_type_binary'])])
                cursor.execute(insert_query_label, query_data_l)
                
            except (Exception, psycopg2.Error) as error :
                print("Failed to insert record (id = " + str(query_data[0]) + ") into mobile table", error)

        conn.commit()
        cursor.close()
        conn.close()



if __name__ == '__main__':
    populate()


