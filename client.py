import hashlib
import sys
import os
import pymysql
import json
#skiplist = ["algo_common","algo_local","algo_tfprotos","opencv_core331","opencv_highgui331","opencv_imgcodecs331","opencv_imgproc331","python36","readresult","zlib"]


def connect_to_mysql():
    db = pymysql.connect(host="192.168.1.149", user="huozhl",password="h81022336",port=3306,database="pvmedcpp",charset='utf8')
    cursor = db.cursor()
    return db,cursor
    
    '''
    '''


def model_check(model_path,model_list):
    all_num = len(model_list.keys())
    tag_num = 0
    for m in model_list.keys():
        m_type = "."+model_list[m][1]
        fs = getallformatfiles(os.path.join(model_path,m),m_type)
        for f in fs:
            if md5sum(f) == model_list[m][-1]:
                #print(f,'match')
                tag_num+=1
    if tag_num == all_num:
        print("Models version match CPP database!")
        return True
    else:
        print("Models version does not match CPP database!")
        return False
               


def analysis(db,cursor,key,model_path):
    sql = "SELECT * FROM pvmed_cpp_manager WHERE md5 = \'{}\';".format(key);
    cursor.execute(sql)
    results = cursor.fetchall()
    cpp_json = {}
    if len(results) > 0:
        for row in results:
            name = row[1]
            version = row[2]
            modules = row[3]
            models = row[4]
            model_list = {}
            mm_str = []
            for i in modules.split(';'):
                if len(i) > 2:
                    mm_str.append(i+';')

            m_str = []
            m_list = models.split(';')
            for model in m_list:
                temp = model.split('-')
                if len(temp)>1:
                    #temp = model.split('-')
                    m_name = temp[0]
                    m_version = temp[1]
                    m_type = temp[2]
                    m_md5 = temp[3]
                    model_list[m_name] = [m_version,m_type,m_md5]
                    m_str.append(m_name+"-"+m_version+"-"+m_type+";")
            if(model_check(model_path,model_list)):
                cpp_json['model'] = m_str 
                #cpp_json = {}
            cpp_json['name'] = name
            cpp_json['version'] = version
            cpp_json['module'] = mm_str
            #cpp_json['model'] = m_str
    return cpp_json
            #else:
                #return {}
            #print(name,version,modules,model_list)
                    

def md5sum(filepath): 
    m = hashlib.md5()
    n = 4096 * 1024 * 1024
    s = ""
    inp = open(filepath,'rb')
    while True:
        buf = inp.read(n)
        if buf:
            m.update(buf)
        else:
            break
        s+=(m.hexdigest())
    inp.close()
    return s

def getallformatfiles(basepath,m_format):
    filelist = []
    for root,dirs,files in os.walk(basepath):
        for f in files:
            if m_format in f.lower():
                filelist.append(os.path.join(root,f))
                #print(f)
    return filelist


def get_python_info(data):
    python_info = {}
    python_info['name'] = data['name']
    python_info['version'] = data['version']
    temp0 = []
    for i in data['module']:
        temp0.append(i['name']+'-'+i['version']+";")
    python_info['module'] = temp0
    temp = []
    for j in data['model']:
        temp.append(j['name']+'-'+j['version']+'-'+j['type']+";")
    python_info['model'] = temp
    return python_info

if __name__ == '__main__':
    std_json = sys.argv[1]
    dll_path = sys.argv[2]
    model_path = sys.argv[3]
    db,cursor = connect_to_mysql()
    
    with open(std_json, 'r') as f:
        data = json.load(f)
    py_info = get_python_info(data)
    #print(data)
    f_type=".so"
    so_files = getallformatfiles(dll_path,f_type)
    for f in so_files:
        if data['name'] in f:
            cpp_info = analysis(db,cursor,md5sum(f),model_path)
            #print(f,cpp_info)
            if(cpp_info != {}):
                '''
                for a in ['name','version','model','module']:
                    print(a)
                    print("cpp_info:",cpp_info[a])
                    print('python_info:',py_info[a])
                '''
                if py_info['name'] in cpp_info['name']:
                    print('File name match!!!')
                else:
                    print('File name unmatch!!!')
                
                if py_info['version'] in cpp_info['version']:
                    print('Global version match!!!')
                else:
                    print('Global version unmatch!!!')

                tag = 0
                for py in py_info['model']:
                    if py not in cpp_info['model']:
                        tag += 1
                        print(py,'not match!!!')
                if tag == 0:
                    print('All models version match!!!')
                tag = 0
                for py in py_info['module']:
                    tag = 0
                    if py not in cpp_info['module']:
                        print(py,'not match!!!')
                if tag == 0:
                    print('All modules version match!!!')


    cursor.close()
    db.close()


