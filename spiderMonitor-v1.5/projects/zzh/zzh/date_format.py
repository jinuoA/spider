# coding=utf-8

import re

def get_publish_date(info_publish_date):      
    if info_publish_date:      
        date = info_publish_date.replace(" ", "")
        date = date.replace(u"年", "-")
        date = date.replace(u"月", "-")
        date = date.replace(u"日", "")
        publish_date_1 = re.findall(r'\d{4}-\d{1,2}-\d{1,2}', date)
        if publish_date_1:       
            item_publish_date = publish_date_1[0]
            return item_publish_date
            
        publish_date_2 = re.findall(r'\d{4}\.\d{1,2}\.\d{1,2}', date)
        if publish_date_2:           
            publish_date = publish_date_2[0]
            item_publish_date = publish_date.replace(".", "-")
            return item_publish_date
            
        publish_date_3 = re.findall(r'\d{4}/\d{1,2}/\d{1,2}', date)
        if publish_date_3:          
            publish_date = publish_date_3[0]
            item_publish_date = publish_date.replace("/", "-")
            return item_publish_date
                                
        return ""  # item_publish_date = ""
    else:
        return ""  # item_publish_date = ""
        
    if item_publish_date:
        print item_publish_date
        item_publish_date = time.strftime("%Y-%m-%d",item_publish_date)
        print item_publish_date
        

                          
                             
                          
                          
                          