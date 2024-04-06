import streamlit as st
import easyocr 
import re
from PIL import Image
import pandas as pd 
import mysql.connector
from sqlalchemy import create_engine
import time
import io
from streamlit_option_menu import option_menu

mydb= mysql.connector.connect(
    host='database-1.cxe2c4iqum5i.ap-south-1.rds.amazonaws.com',
    user="admin",
    password="Surya0807sada",
    database='bizcard')
mycursor= mydb.cursor()

st.set_page_config(page_title= "BizCardX",
                   page_icon= '💼',
                   layout= "wide",)   

def image_processing(img):
  Image_result=[]
  for (bbox,text,prob) in img:
      Image_text=text
      Image_result.append(Image_text)
  Image_data = {
        "name": [],
        "designation": [],
        "contact": [],
        "email": [],
        "website": [],
        "street": [],
        "city": [],
        "state": [],
        "pincode": [],
        "company": [],
        "other":[] 
        }

  for i in range(len(Image_result)):
    name=r'\b[a-zA-Z\s]+\b'
    designation=r'\b[A-Za-z\s]+\b'
    phonenumber=r'\b(?:\+?\d{1,3}[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b'
    mail=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    streetname_1 = re.findall('([0-9]+ [A-Z]+ [A-Za-z]+)., ([a-zA-Z]+). ([a-zA-Z]+)',Image_result[i])
    street_name = re.findall('([0-9]+ [A-Za-z]+ [A-Za-z]+)., ([a-zA-Z]+)', Image_result[i])
    pincode_name= re.findall('([A-Za-z]+) ([0-9]+)',Image_result[i])
    pincode_1 = re.findall('^\d{6}$', Image_result[i])
    ph=[]
    
    if i==0:
      Image_data['name'].extend(re.findall(name, Image_result[i]))  
    elif i==1:
      title=re.findall(designation,Image_result[i])
      Image_data["designation"].append(title[0])
    elif '-' in Image_result[i]:
      phone= re.findall(phonenumber,Image_result[i])
      ph.extend(phone)
      Image_data["contact"].extend(ph)
    elif '@'in Image_result[i]:
      Image_data["email"].append(Image_result[i])   
    elif "www."in Image_result[i].lower() or "www" in Image_result[i].lower() or "." in Image_result[i].lower():
         Image_data["website"].append(Image_result[i]) 
    elif streetname_1:
      Image_data["street"].append(streetname_1[0][0])
      Image_data["city"].append(streetname_1[0][1])  
      Image_data["state"].append(streetname_1[0][2])     
    elif street_name:
        Image_data["street"].append(street_name[0][0])
        Image_data["city"].append(street_name[0][1])
    elif pincode_name:
        Image_data['state'].append(pincode_name[0][0])
        Image_data["pincode"].append(pincode_name[0][1])
    elif pincode_1:
        Image_data["pincode"].append(pincode_1[0])
    else:
       Image_data['other'].append(Image_result[i])
  Image_data["contact"]=['  & '.join(Image_data["contact"])]
  return(Image_data)

def image_binary(img):
    binarydata=img.read()
    return binarydata
  
with st.sidebar:
    selected = option_menu("Menu", ["About us","Upload","Action"], 
        icons=['house', 'cloud-upload',"list-task"], menu_icon="cast", default_index=0)
      
if selected=="About us":
  st.title("Biz_Card")
  st.write("Where Paper Meets Pixels, and Networking Becomes Effortless!")
  st.header("Welcome to Business Card App")
  st.write(''' We're thrilled to introduce you to a groundbreaking solution 
           poised to revolutionize the management of your contact information.
           Our innovative project is designed to simplify the process of storing 
           and accessing business cards by establishing a comprehensive digital database.
           Our BizCard Project not only offers a streamlined approach to 
           contact management but also eliminates the need for physical storage.
           By reducing the risk of misplacing important cards, our digital database 
           guarantees the preservation of your invaluable connections for the long haul.''')
  st.header("Technology List ")
  st.markdown(''' 
                - Python
                - OCR
                - MYSQL(AWS)
                - Streamlit''')
  st.header("Tutorial")
  st.markdown(''' 
                - Upload Business Card Image
                - Extract Relevant Information
                - Display Extracted Information
                - Save Information to Database
                - Read,Update and Delete Data''')
    
if selected=="Upload":   
     st.header("Upload-Store-Connect")
     st.title("Image Text Extractor")
     uploaded_file=st.file_uploader("Select a Image file",type=["jpg","jpeg","png"])
     if uploaded_file is not None: 
          reader = easyocr.Reader(['en'])
          image = uploaded_file.read()
          result = reader.readtext(image) 
          aa = Image.open(uploaded_file)
          st.header("Card Image")
          col = st.columns((4, 3), gap='medium')
          
          with col[0]:
              st.image(aa)
              output = image_processing(result)
              st.header('Extracted information')
              Name = st.text_input("Cardholder Name", *output['name'])
              job_role = st.text_input("Cardholder Role", *output['designation'])
              contact_details = st.text_input("Contact Number", *output['contact'])
              Email_id = st.text_input("Email_Id", *output['email'])

          with col[1]:
              website = st.text_input("Website", output['website'])
              street = st.text_input("Address", *output['street'])
              city = st.text_input("City Name", *output['city'])
              state = st.text_input("State Name", *output['state'])
              pincode = st.text_input("Postcode", *output['pincode'])
              company = st.text_input("Company Name")
              other_info = st.text_input("other", output['other']) 
              Image = image
              CardDetail = {
                  'Card_Name': Name,
                  'Title': job_role,
                  'Contact': contact_details,
                  'Email': Email_id, 
                  'Website': website, 
                  'Street': street,
                  'City': city, 
                  'state': state,
                  'Pincode': pincode,
                  'Company': company,
                  'Image': Image
              }

          mycursor.execute("SELECT Company FROM carddetail")
          result = mycursor.fetchall()
          company_name = [x[0] for x in result]
          company_name.sort()

          def migrate_sql():
              card_info = pd.DataFrame(CardDetail, index=[0])
              engine = create_engine("mysql+mysqlconnector://{user}:{pw}@{host}/{db}".format(user="admin", pw="Surya0807sada", host="database-1.cxe2c4iqum5i.ap-south-1.rds.amazonaws.com", db="bizcard"))
              card_info.to_sql('carddetail', con=engine, if_exists="append", chunksize=1000, index=False)          
              return ("Card has been Successfully Stored")       

          if st.button('Migrate to SQL'):
              if CardDetail["Company"] in company_name:
                  st.write("Already exists in databases")
                       
              else:
                  st.write(migrate_sql())
                  
     

if selected=="Action":           
       mycursor.execute("SELECT Card_Name from carddetail" )
       result=mycursor.fetchall()
       person=[x[0] for x in result]
       person.sort() 
       selected_contact=st.selectbox("ContactName",person,index=None)
       action=["View","Update","Delete"]
       select_action=st.selectbox("Action",action,index=None)
       if select_action=="View":
         if selected_contact is not None:
              mycursor.execute("SELECT * from carddetail WHERE Card_Name=%s;",(selected_contact,) )
              result=mycursor.fetchone()
              view=pd.DataFrame([result], columns=["Name","Designation","Contact","Email","Website","Street","City","state","pincode","company","image"])
              st.write(view)
         else: 
           st.error("please select Contact Name")
           
       if select_action=="Update":
         if selected_contact is not None:
            mycursor.execute("SELECT * from carddetail WHERE Card_Name=%s;",(selected_contact,) )
            modify=mycursor.fetchone()
            mod_Name = st.text_input("Cardholder Name", modify[0], key="mod_Name")
            mod_job_role = st.text_input("Cardholder Role", modify[1], key="mod_job_role")
            mod_contact_details = st.text_input("Contact Number", modify[2], key="mod_contact_details")
            mod_Email_id = st.text_input("Email_Id", modify[3], key="mod_Email_id")
            mod_website = st.text_input("Website", modify[4], key="mod_website")
            mod_street = st.text_input("Address", modify[5], key="mod_street")
            mod_city = st.text_input("City Name", modify[6], key="mod_city")
            mod_state = st.text_input("State Name", modify[7], key="mod_state")
            mod_pincode = st.text_input("Postcode", modify[8], key="mod_pincode")
            mod_company = st.text_input("Company Name", modify[9], key="mod_company")
            if st.button("submit"):
                query = f"update carddetail set Card_Name = %s, Title = %s, Contact = %s, Email = %s, Website = %s, " \
                              f" Street = %s, City=%s, state=%s,Pincode = %s,Company=%s where Card_Name = '{selected_contact}'"
                val = (mod_Name, mod_job_role, mod_contact_details,mod_Email_id,mod_website,mod_street,mod_city,mod_state,mod_pincode,mod_company)
                mycursor.execute(query,val)
                mydb.commit()
                st.success("Changes has been updated successfully in database",icon="✅")
         else:
           st.error("please select Contact Name")
           
       if select_action=="Delete":
         if selected_contact is not None:
           confirmation = st.radio("Are you sure you want to delete?,It will delete permanently from database", ("Yes", "No"),index=None)
           if confirmation=="Yes": 
              mycursor.execute("DELETE from carddetail WHERE Card_Name=%s;",(selected_contact,) )
              mydb.commit()
              st.success(" successfully deleted database",icon="✅")
           if confirmation=="No":
               st.write("Thank you") 
         else:
           st.error("please select Contact Name")
                    
       
       
       
            
  
   
  