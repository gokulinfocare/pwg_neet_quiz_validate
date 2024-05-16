# This program uses XML data and use streamlit to update the data and then generate a new XML file
# Have to change the path mentioned for saving updated XML file
import streamlit as st 
import xml.etree.ElementTree as ET
import sys
import pandas as pd
import os
from function_moodle_xml_create import create_moodle_xml

# Function to get data from XML file
def get_data_from_xml():

    xml_table = []              # List to store the data from XML file
    new_filename = "updated.xml"   # Default name for updated XML file
    
    st.set_page_config(page_title="Please upload XML file to display/edit the data", layout="wide")
    
    file_name = st.file_uploader("Choose the XML file you want to display/edit")
    if file_name is not None:
        file_contents = file_name.read().decode("utf-8")
        root = ET.fromstring(file_contents)
        xml_table = []
        #Takes data from the XML file uploaded and stores it in a list of dictionaries
        for element in root.findall('.//question'):
            if element.attrib['type'] == 'multichoice':
                moodle_id = qtext = soln = option1 = option2 = option3 = option4 = answer = ''     
                moodle_id = element.find('.//name/text').text
                qtext = element.find('.//questiontext/text').text
                soln = element.find('.//correctfeedback/text').text
                w_count = 1
                w_incorrect_feedback = ""
                xml_feedback = ""
                for rec in element.findall('.//answer'):
                    if w_incorrect_feedback == "":
                        if rec.find('feedback/text') is not None:
                            xml_feedback = rec.find('feedback/text').text
                        if xml_feedback is not None:
                            w_incorrect_feedback = xml_feedback
                    if w_count == 1:
                        option1 = rec.find('text').text
                        if rec.attrib['fraction'] == '100':
                            answer = 'A'
                    elif w_count == 2:
                        option2 = rec.find('text').text
                        if rec.attrib['fraction'] == '100':
                            answer = 'B'
                    elif w_count == 3:
                        option3 = rec.find('text').text
                        if rec.attrib['fraction'] == '100':
                            answer = 'C'
                    elif w_count == 4:
                        option4 = rec.find('text').text
                        if rec.attrib['fraction'] == '100':
                            answer = 'D'
                    w_count += 1
                struc = {
                    'moodle_id': moodle_id,
                    'questiontext': qtext,
                    'soln': soln,
                    'option1': option1,
                    'option2': option2,
                    'option3': option3,
                    'option4': option4,
                    'answer': answer,
                    'incorrect_feedback': w_incorrect_feedback
                }
                xml_table.append(struc)
        # Get the filename from the file_uploader widget
        filename = file_name.name
        
        # Get the file extension
        file_extension = filename.split(".")[-1]
        
        # Create the new filename with "_updated.xml" suffix
        new_filename = filename.replace(f".{file_extension}", "_updated.xml")
        
        # Check if the number of records is 50
        if len(xml_table) != 50:
            print("50 records not found in XML file")
            sys.exit()
        
    return xml_table , new_filename         # Return the data and new filename

# Function to display original data 
def display_data(data):
    st.write("### Original Data:")
    st.dataframe(data)

# Function to edit data
def edit_data(data):
    st.write("### Edit Data:")
    num_rows = len(data)

    # Get column names from the keys of the first dictionary in the list
    if num_rows > 0:
        column_names = list(data[0].keys())
    else:
        column_names = []

    # Create empty DataFrame with columns
    edited_data = pd.DataFrame(columns=column_names, index=range(num_rows))
    data = pd.DataFrame(data)           #Convert the list of original data to a dataframe
    for i in range(len(data)):
        for col in data.columns:
            if len(data.at[i, col]) > 180:     #If the length of the data is more than 180 chars
                edited_data.at[i, col] = st.text_area(f"Row {i+1} - {col}", data.at[i, col],  height=175)
            else:
                edited_data.at[i, col] = st.text_input(f"Row {i+1} - {col}", data.at[i, col])   #Edits the data in the dataframe
    return edited_data


def create_xml(data,new_filename):
    
    tree = create_moodle_xml(data)
    #Write the ElementTree object to an XML file mentioning path name
    #file_path = f"C:/Users/Taanya/Desktop/AssignGokul/Streamlit/{new_filename}"
    # file_path = f"C:/Moodle Files/Languages/{new_filename}"
    # with open(file_path, 'w', encoding='utf-8') as file:
    #     file.write(tree)
    #xml_string = ET.tostring(tree, encoding="utf-8")    
    st.download_button(label="Save Changes and Download XML File ", data=tree, file_name=new_filename)

    #st.write("### Updated XML file has been created successfully!")

# Main
st.header = "Program to Update Quiz Data"
st.title("Please upload XML file to display/edit the data")
xml_table, new_filename = get_data_from_xml()       #Get the data from the XML file
if len(xml_table) > 0 :
    display_data(xml_table)                             #Display the original data
    updated_data = edit_data(xml_table)                 #Edit the data
    if updated_data is not None:
            st.write("### Updated Data:")
            st.dataframe(updated_data)
    xml_data = updated_data.to_dict('records')          #Converting the updated data dataframe to dictionary format
    
    # Call the function with the updated data
    #if st.button('Save Changes and Download File'):                       # Button to save changes one time only, so that multiple changes are saved.
    create_xml(xml_data,new_filename)               #Once submitted, the updated XML file is created and saved in the folder path mentioned
