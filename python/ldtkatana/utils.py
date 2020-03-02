"""
.. module:: katana
   :synopsis: general katana utilities.

.. moduleauthor:: Ezequiel Mastrasso

"""
from Katana import Widgets, FnGeolib, Nodes3DAPI, NodegraphAPI

def get_locations(node, search_location, cel_expression):
    """
    Get all locations matching a cel_expression, at a node and at a given scene graph location.

    Args:
        node (str): node name
        seach_location (str): Scene graph location
        cel_expression (str): CEL expression
    
    Returns:
        array. matched location paths

    """
    collector = Widgets.CollectAndSelectInScenegraph(cel_expression, search_location)
    matchedLocationPaths = collector.collectAndSelect(select=False, node=node)
    return matchedLocationPaths

def get_selected_nodes(single=False):
    """
    Get selected nodes from the node graph, if single is given will
    check if a single node is selected.

    Kwargs:
        single (bool): single node selection
    
    Returns:
        list. Selected nodes.
    
    #FIXME (eze) this should return arrays, even is single is on
    """
    nodes = NodegraphAPI.GetAllSelectedNodes()
    if single:
        if len(nodes) != 1:
            raise RuntimeError("Please select 1 node.")
        return nodes[0]
    else:
        return nodes

def get_attribute_values(node, locations, attribute_name):
    """
    Get unique attribute values from locations.

    Given a list of locations, and an attribute name, it cooking the locations at
    the given node, and gets a list of unique values for the attribute_name.
    
    Args:
        node (str): node
        locations (list): locations to cook
        attribute_name (str): Attribute name to fetch
    
    Returns:
        list. List of unique attributes

    """
    runtime = FnGeolib.GetRegisteredRuntimeInstance()
    txn = runtime.createTransaction()
    client = txn.createClient()
    op = Nodes3DAPI.GetOp(txn, NodegraphAPI.GetNode(node.getName()))
    txn.setClientOp(client, op)
    runtime.commit(txn)

    attribute_values = []

    for location in locations:
        cooked_location = client.cookLocation(location)
        attrs = cooked_location.getAttrs()
        attribute = attrs.getChildByName(attribute_name)
        attribute_value = attribute.getChildByName("value").getValue()
        if attribute_value not in attribute_values:
            attribute_values.append(attribute_value)
    return attribute_values

def get_objects_attribute_values(node, attribute_name):
    """
    List object at a given view node, that have a particular attribute.
    
    Args:
        node (str): view node
        attribue_name (str): attribute name to search
    
    Returns:
        list. list of unique attributes values

    """
    cel_expression = '//*{ hasattr("%s") }' % attribute_name
    search_location = "/root/world"
    attribute_locations = get_locations(node, search_location, cel_expression)
    return get_attribute_values(node, attribute_locations, attribute_name)

def add_node_to_group_last(group_node, node, inputPort="in", outputPort="out"):
    """
    Insert a node as last, into a group.
    
    Insert a node as the last node before the outputPort.
    Input port not really required, but requires to be specified, as it has a
    different default name that other group like nodes.

    Args:
        group_node (str): group node to add a node
        node (str): node to add

    Kwargs:
        inputPort (str): in port of the group node
        outputPort (str): group output port
    
    """
    node.setParent(group_node)
    node_inputPort = node.getInputPort(inputPort)
    node_outputPort = node.getOutputPort(outputPort)
    group_node_sendPort = group_node.getSendPort(inputPort)
    group_node_returnPort = group_node.getReturnPort(outputPort)

    last_out = group_node_returnPort.getConnectedPorts()[0]
    last_out.connect(node_inputPort)
    node_outputPort.connect(group_node_returnPort)