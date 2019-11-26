import numpy as np
import matplotlib.pyplot as pyp
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import random as rd
import pandas as pd
import psycopg2
from psycopg2 import sql


# Define Kernel
def K(M,z):
    
    ''' Kernel
        z : vector
        M to distort geometry'''
    
    result = (2*np.pi)**(-2/2) * np.exp(-np.dot(z,np.dot(M,z))/2) # numpy transpose automatically
    return(result)

##
##def difference(x, y):
##    
##    ''' distance between vector x and y '''

    

    
def dens(x, data, h, M = np.array([[1,0],[0,1]])):
    
    ''' Density
        x : vector
        data : as the name perfectly describe it
        h : window width
        
        M = 1  # dimension 1 
        M = np.array([[1,0],[0,1]])  # dimension 2 simple euclidian geometry
        
        Return the density of the vector as part of data with a given geometry and window width'''
    
    n = len(data)
    density = 0
    for a in range(n):
        density += K(M, (np.array(x)-np.array(data[a]))/h)
    density = density/(n*h**2)
    return(density)



##nb_point = 100
##
####absc = [np.linspace(0,15,nb_point), np.linspace(-15,15,nb_point)]
##absc = [np.linspace(-1,6,nb_point), np.array([ 0 for a in range(nb_point) ])]
##
##absc = list(zip(absc[0], absc[1]))
##
##density = []
##for a in range(len(absc)):    
##    density.append(dens(absc[a], data, 1))


def generateInterval(lim_inf = [-15,-15], lim_sup = [15,15], indent = 0.2):
    
    ''' Generate couple of intervals
        Not general function, adapted to 2 dimension label
        hardly scalable'''
    
    listInterv = []
    debut1 = lim_inf[0]
    debut2 = lim_inf[1]
    last1 = debut1 + indent
    last2 = debut2 + indent
    epsilon = 0.001
    while last1 <= lim_sup[0]+epsilon:
        while last2 <= lim_sup[1]+epsilon:
##            print([[debut1, last1],[debut2, last2]])
            listInterv.append([[debut1, last1],[debut2, last2]])
            debut2 = last2
            last2 = last2 + indent
            
##        print(debut1,last1)
        debut1 = last1
        last1 = last1 + indent
        debut2 = lim_inf[1]
        last2 = debut2 + indent

    return(listInterv)

def generateIntervalDensity(list_density, subdiv = 10):
    
    ''' Generate interval : regular in that case, but could be optimized
        list_density : list in that case  for each sample '''

    list_density = np.array(list_density)
    interv = np.linspace(list_density.min()-0.1,list_density.max()+0.1, subdiv)

    return(interv)

def checkIntervalDensity(dens, listInterv):
    
    ''' return with string version of the intervals containing dens
        return 'None' if not '''
    
    intervalIdentifier = -1
    indi = 0
    while intervalIdentifier == -1 and indi<=len(listInterv)-2:
        if listInterv[indi+1]>dens and dens>listInterv[indi]:
            intervalIdentifier = indi
        indi+=1
    if intervalIdentifier == -1:
        return("None")
    else:
        return(str([listInterv[intervalIdentifier],listInterv[intervalIdentifier+1]]))

def checkInterval(x, y, listInterv):
    
    ''' return with string version of the intervals containing x and y
        return 'None' if not '''
    
    intervalIdentifier = -1
    indi = 0
    while intervalIdentifier == -1 and indi<=len(listInterv)-1:
##        print(indi, listInterv[indi][0][0], listInterv[indi][0][1], listInterv[indi][1][0], listInterv[indi][1][1])
        if listInterv[indi][0][1]>x and x>listInterv[indi][0][0] and listInterv[indi][1][1]>y and y>listInterv[indi][1][0]:
            intervalIdentifier = indi

        indi+=1
    if intervalIdentifier == -1:
        return("None")
    else:
        return(str(listInterv[intervalIdentifier]))
               

#dd = checkInterval(-10, 5, gg)

def search_on_grid(data, lim_inf = [-15,-15], lim_sup = [15,15]):
    
    ''' building distinct intervals
    Store the sample_id of the contained in those spaces
    sampled_id are classified regarding their density
    Default adapted to our toy project with only 2 labels

    not complete... to be refactored

    '''

    # generate intervals
    grid = generateInterval(lim_inf, lim_sup)

    dict_id = {}

    for dat in data:
        inte = checkInterval(dat[1], dat[2], grid)
        try:
            dict_id[inte].append(dat[0])
        except:
            dict_id[inte] = []
            dict_id[inte].append(dat[0])

    return(dict_id)


def sample_label_density(data):
    
    '''return sample_id ordered by sample labels density
        Not optimal, we go through data three times... and extreme value sensitive.'''

    dict_id = {}



    data_refa = []
    density_list = []
    length = len(data)
    for a in range(length):
        data_refa.append(np.array([data[a][1], data[a][2]]))
        
    # density intervals
    for a in range(length):
        density_list.append(dens(data_refa[a], data_refa, 1))

    intervals = generateIntervalDensity(density_list, subdiv = 10)

    for dat in data:
        inte = dens(data_refa[a], data_refa, 1)
        inte = checkIntervalDensity(inte, intervals)
        
        try:
            dict_id[inte].append(dat[0])
        except:
            dict_id[inte] = []
            dict_id[inte].append(dat[0])

    return(dict_id)


def partition(dbname, num_partition):
    
    '''  dispath the data in order to approximatively preserve 
    the original disttibution'''
    
    try:
        conn=psycopg2.connect("dbname="+dbname +" user='postgres' host='localhost' password='test'")
    except:
        print("I am unable to connect to the database.")


    if (conn):
        cursor = conn.cursor()
        # load everything on RAM
        cursor.execute('SELECT * FROM label')
        #one = cursor.fetchone()

        all_labels = cursor.fetchall()

        
        # selection regarding coordinate (label_1, label2) on a grid
        dict_id = search_on_grid(all_labels)

##        # selection regarding density of the vector (label_1, label2)
##        dict_id = sample_label_density(all_labels)
        

        #not beautiful, create other tables with the same structure and in the same database, just for prototype

        name_table = []
        for a in range(num_partition):
            # we could assume tables are not created yet
            cursor.execute("select * from information_schema.tables where table_name=%s", ('label' + str(a),))
            if not bool(cursor.rowcount):
                cursor.execute("CREATE TABLE sample" + str(a) + " (sample_num integer PRIMARY KEY,dim_1 real,dim_2 real,dim_3 real,dim_4 real,dim_5 real);")
                cursor.execute("CREATE TABLE label" + str(a) + " (sample_num integer REFERENCES sample" + str(a) + " (sample_num),sample_type integer,sample_type_binary integer,PRIMARY KEY (sample_num));")
            name_table.append(["sample" + str(a), "label" + str(a)])




        for interval in dict_id.keys():
            count = 0
            for sample_id in dict_id[interval]:
                name = name_table[count%num_partition]

                # to be enhanced, we once again ask the database...
                cursor.execute('SELECT * FROM sample WHERE sample_num='+str(sample_id)+";")
                row = cursor.fetchone()         
                cursor.execute(sql.SQL("INSERT INTO {} VALUES (%s,%s,%s,%s,%s,%s)").format(sql.Identifier(name[0])),row)

                cursor.execute('SELECT * FROM label WHERE sample_num='+str(sample_id)+";")
                row = cursor.fetchone()         
                cursor.execute(sql.SQL("INSERT INTO {} VALUES (%s,%s,%s)").format(sql.Identifier(name[1])),row)
##                print(sample_id, row)
                count += 1


        conn.commit()
        cursor.close()
        conn.close()





#partition("dbtoy", 2)

##
### illustrate 2D  
##
##absc_unzip = [[ i for i, j in absc ], [ j for i, j in absc ]] 
##
####absc_unzip = [[ i for i, j in absc ], [ 0 in range(len(absc)) ]]
##density = np.array(density)
##
##
##pyp.figure()
##pyp.plot(absc_unzip[0], density)
##pyp.show()
##pyp.close()
##
##y_ord2 = []
##
##for a in range(len(absc_unzip[0])-2): # pas très efficace
##    y_ord2.append(np.trapz(density[0:a+2],absc_unzip[0][0:a+2]))
##
##y_ord2 = np.array(y_ord2)
##
##
##
### cumulate plot
##pyp.figure('2')
##pyp.plot(absc_unzip[0][:-2],y_ord2)
##pyp.show()
##pyp.close()

















##X, Y = np.meshgrid(data_unzip[0], data_unzip[1])
##fig = pyp.figure()
##ax = pyp.axes(projection='3d')
##ax.contour3D(X, Y, density, 50, cmap='binary')
##ax.set_xlabel('x')
##ax.set_ylabel('y')
##ax.set_zlabel('z')
##pyp.show()
##pyp.close()



##fig = pyp.figure()
##ax = fig.gca(projection='3d')
##surf = ax.plot_surface(data_unzip[0], data_unzip[1], density, rstride=1, cstride=1,cmap=cm.autumn,
##                       linewidth=0, antialiased=False, alpha =.1)
####ax.plot_surface(data_unzip[0], data_unzip[1], density, 
####              cmap=cm.coolwarm,
####              linewidth=0, 
####              antialiased=True)
##ax.set_xlabel('x')
##ax.set_ylabel('y')
##ax.set_zlabel('z')
##pyp.show()


### 3d plot
##fig = pyp.figure()
##ax = pyp.axes(projection='3d')
##ax.plot3D(data_unzip[0], data_unzip[1], density)
##pyp.show()
##pyp.close()

# 2d plot





### generate data, normal distribution
##data = [rd.gauss(0,2) for a in range(1000)]
##
### uniform distribution
##data_uni = [rd.uniform(-15,15) for a in range(3000)]


# abscisse/ordonnée
##x_absc = np.linspace(-15,15,250)
##y_ord = []
##for a in range(len(x_absc)):
##    y_ord.append(dens(x_absc[a],data,3))
##
##y_ord = np.array(y_ord)
##
##
### cumulate function
##y_ord2 = []
##
##for a in range(len(x_absc)-2): # pas très efficace
##    y_ord2.append(np.trapz(y_ord[0:a+2],x_absc[0:a+2]))
##
##y_ord2 = np.array(y_ord2)
##
##
### density plot
##pyp.figure('1')
##pyp.plot(x_absc,y_ord)
##pyp.show()
##pyp.close()
##
### cumulate plot
##pyp.figure('2')
##pyp.plot(x_absc[0:-2],y_ord2)
##pyp.show()
##pyp.close()
