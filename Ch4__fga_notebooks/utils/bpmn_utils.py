import os, warnings
import xml.etree.ElementTree as ET
import xmltodict


SYSTEM_DIR_SEP = '\\'
BASE_DIR = r'C:\DEV\NASSY\nassy-eyemind_plus-beta\utils' + SYSTEM_DIR_SEP
BPMN_DATA_DIR = BASE_DIR + r'bpmn_utils_data' + SYSTEM_DIR_SEP


###
# BPMN DEFINITION
# XML namespaces.
###
XMLNS = {
    'bpmn':"http://www.omg.org/spec/BPMN/20100524/MODEL",
    'bpmndi': "http://www.omg.org/spec/BPMN/20100524/DI",
    'dc': "http://www.omg.org/spec/DD/20100524/DC",
    'di': "http://www.omg.org/spec/DD/20100524/DI"
}
CAMUNDA = {
    'modeler': "http://camunda.org/schema/modeler/1.0"
}


###############################################################################
###
# Load BPMN files
###
def list_bpmn_files(dir_path, b_absolute_path):
    # Returns a list of bpmn files in dir_path
    
    # retrieve all files in dir_path
    absolute_path = dir_path + SYSTEM_DIR_SEP if b_absolute_path else ''
    res = []
    try:
        for file_path in os.listdir(dir_path):
            if os.path.isfile(os.path.join(dir_path, file_path)):
                res.append((file_path, [absolute_path]))
    except FileNotFoundError:
        print(f"The directory {dir_path} does not exist")
    except PermissionError:
        print(f"Permission denied to access the directory {dir_path}")
    except OSError as e:
        print(f"An OS error occurred: {e}")

    # filter for bpmn files only
    res = dict(a_file_tuple for a_file_tuple in res if a_file_tuple[0].endswith('.bpmn'))

    return res
# DEF: list_bpmn_files


def extract_bpmn_actvities(model_root):
    # Parse xml content of a bmpn file to retrieve the activities

    task_dict = {}
    nb_tot_tasks= 0
    nb_activity = 0

    for task in model_root.iter(f"{{{XMLNS['bpmn']}}}task"):
        nb_tot_tasks += 1

        task_attrib = {'name': task.get('name', "Activity_"+str(nb_tot_tasks))}
        task_dict[task.get('id')] = task_attrib
    # FOR: task

    for shape in model_root.iter(f"{{{XMLNS['bpmndi']}}}BPMNShape"):
        if shape.attrib['bpmnElement'].startswith("Activity"):
            bounds = shape.find('dc:Bounds', XMLNS)

            task_id = shape.get('bpmnElement')
            if task_id in task_dict.keys():
                nb_activity += 1
                # the attribute 'bpmnElement' correspond to the id of the
                # element in the process part
                task = task_dict[shape.get('bpmnElement')]

                task['bounds'] = (int(bounds.get('x')), int(bounds.get('y')), 
                                int(bounds.get('width')), int(bounds.get('height')))
        else:
            # Unknown or unsupported.
            pass
    # FOR: shape

    if nb_tot_tasks != nb_activity:
        print(f'Attention: {nb_tot_tasks} found. {nb_activity} found.')

    return task_dict
# DEF: extract_bpmn_actvities

def parse_bpmn_element(dict):
    # Parse xml content of a bmpn file

    _dict = {}

    for attrib, val in dict['bpmn:definitions']['bpmn:process'].items():
        # print(attrib)
        
        # Test the attribute...
        if attrib.startswith('@'): #  ... is a property of the parent.
            # it's a property
            # Nothing to to.
            pass
        elif attrib.startswith('bpmn'): # ... is a BPMN element
            match attrib:
                case 'bpmn:documentation':
                    # Nothing to do
                    pass
                case _:
                    # it's an element
                    if not isinstance(val, list):
                        val = [val]

                    for e in val:
                        _dict[e['@id']] = e
        else:
            # the attribute is gnored
            warnings.warn(f'Unknonw attibute ("{attrib}". Will be ignored.)') 

    # print(_dict)



    # task_dict = {}
    # nb_tot_tasks= 0
    # nb_activity = 0

    # for task in model_root.iter(f"{{{XMLNS['bpmn']}}}task"):
    #     nb_tot_tasks += 1

    #     task_attrib = {'name': task.get('name', "Activity_"+str(nb_tot_tasks))}
    #     task_dict[task.get('id')] = task_attrib
    # # FOR: task

    # for shape in model_root.iter(f"{{{XMLNS['bpmndi']}}}BPMNShape"):
    #     if shape.attrib['bpmnElement'].startswith("Activity"):
    #         bounds = shape.find('dc:Bounds', XMLNS)

    #         task_id = shape.get('bpmnElement')
    #         if task_id in task_dict.keys():
    #             nb_activity += 1
    #             # the attribute 'bpmnElement' correspond to the id of the
    #             # element in the process part
    #             task = task_dict[shape.get('bpmnElement')]

    #             task['bounds'] = (int(bounds.get('x')), int(bounds.get('y')), 
    #                             int(bounds.get('width')), int(bounds.get('height')))
    #     else:
    #         # Unknown or unsupported.
    #         pass
    # # FOR: shape

    # if nb_tot_tasks != nb_activity:
    #     print(f'Attention: {nb_tot_tasks} found. {nb_activity} found.')

    return _dict
# DEF: parse_bpmn_element



def load_bpmn_file(fName, fPath=''):
    # Load a bpmn file
    # It returns the content as xml tree object and a dictionary of the 
    # activities in the model.

    tree = ET.parse(fPath+fName)
    [ET.register_namespace(k, v) for k,v in XMLNS.items()] # usefull for writing
    [ET.register_namespace(k, v) for k,v in CAMUNDA.items()] # usefull for writing
    root = tree.getroot()

    activity_dict = extract_bpmn_actvities(root)
    
    return tree, activity_dict

def load_bpmn_file(fName, fPath=''):
    # Open the file and read the contents
    with open(fPath + fName, 'r', encoding='utf-8') as f:
        _xml = f.read()

    
    # Use xmltodict to parse and convert the XML document
    dict = xmltodict.parse(_xml)

    # extract all elements in a secondary dictionary
    elements = parse_bpmn_element(dict)

    return dict, elements






###############################################################################
# End of file
#
def main_exec():
    print("--> Running main_exec function.\n")

    fName = 'simple2.bpmn'
    dict, elements = load_bpmn_file(fName, BPMN_DATA_DIR)

    print('General dictionary')
    for attrib, val in dict['bpmn:definitions']['bpmn:process'].items():
        print(attrib)


    print('Secondary dictionary')
    for id, val in elements.items():
        print(f'{id}:{val}')





def import_exec():
    print("--> Importing bpmn_utils module file.\n")
 
if __name__ == "__main__": main_exec()
else: import_exec()