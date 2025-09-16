from api.forsta_api_utils import upload_project_file, download_project_file

# x = download_project_file(
#     project_path=f"/selfserve/2222/xml_upload_test_2",
#     kind="xml"
# )


upload_project_file(
    project_path=f"/selfserve/2222/xml_upload_test_2", 
    filepath="xml/xml_upload_test_2_xml_confidential.xml", 
    output_filename="survey.xml"
    )

