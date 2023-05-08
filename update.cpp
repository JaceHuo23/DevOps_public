#include <iostream>
#include <string>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/foreach.hpp>
#include <vector>
#include <fstream>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <mysql.h>

using namespace boost::property_tree;
using namespace std;


string key,name,version,module,model,info;

int ParseJson(string str,string f_dir,string model_dir)
{
    //string f_dir = "./lib";
    //string model_dir = "./model";
    stringstream ss(str);
    ptree pt;
    try{
        read_json(ss,pt);
    }
    catch(ptree_error & e){
        return 1;    
    }

    try{
        name = pt.get<string>("name");
        cout<<"name:"<<name<<endl;

		FILE* fpk = NULL;
        char kcmd[512],kres[512];
        sprintf(kcmd, ("md5sum "+ f_dir +"/" + name).c_str());
        string kst;
        if ((fpk = popen(kcmd, "r")) != NULL)
        {
            fgets(kres, sizeof(kcmd), fpk);
            pclose(fpk);
            kst = kres;
        }
        key = kst.substr(0,32);
        cout<<"key:"<<key<<endl;

        version = pt.get<string>("version");
        cout<<"version:"<<version<<endl;
        module = "";  
        ptree modules_temp = pt.get_child("module");
        BOOST_FOREACH(boost::property_tree::ptree::value_type &v,modules_temp)
        {
            stringstream s;
            write_json(s, v.second);
            ptree pt_temp;
            read_json(s,pt_temp);
            module+=pt_temp.get<string>("name")+"-"+pt_temp.get<string>("version")+";";
        }
        cout<<"module:"<<module<<endl;
        
        model = "";
        ptree model_temp = pt.get_child("model");

        BOOST_FOREACH(boost::property_tree::ptree::value_type &v,model_temp)
        {
            stringstream s;
            write_json(s, v.second);
            ptree pt_temp;
            read_json(s,pt_temp);
			FILE* fp = NULL;
            char cmd[512],res[512];
        	sprintf(cmd, ("md5sum "+ model_dir +"/" + pt_temp.get<string>("name") + "/*."+pt_temp.get<string>("type")).c_str());
        	string st;
            if ((fp = popen(cmd, "r")) != NULL)
        	{
                fgets(res, sizeof(cmd), fp);
                pclose(fp);
                st = res;
            }
			
            model+=pt_temp.get<string>("name")+"-"+pt_temp.get<string>("version")+"-"+pt_temp.get<string>("type")+"-"+st.substr(0,32)+";";
        }
        cout<<"model:"<<model<<endl;
    
    info = pt.get<string>("info");
    cout<< info << endl;

    }
    catch(ptree_error & e){
        return 2;    
    }
    return 0;
}



int main(int argc,char* argv[])
{
	ifstream read;
	read.open(argv[1]);
	string json = "";
	string temp;
	while(getline(read,temp))
		json+=temp;

	ParseJson(json,sys.argv[2],sys.argv[3]);
    
    MYSQL conn;
    mysql_init(&conn);
    if(mysql_real_connect(&conn,"192.168.1.149","huozhl","h81022336","pvmedcpp",3306,NULL,0) == NULL)
        cout<< "Fail:" << mysql_error(&conn) <<endl;
    mysql_query(&conn,"SET NAMES UTF8"); 
    string sql = "INSERT INTO pvmed_cpp_manager (md5,name,version,modules,models,info) values ('" + key + "','" + name + "','" + version + "','" + module+ "','" + model+ "','" + info +"');";
    //cout<<sql.c_str()<<endl;
    mysql_query(&conn,sql.c_str());

	return 0;
}
