import maya.cmds as cmds
import maya.mel as mel

def copy_skin_weights(source, target):
    """
    Function to copy skin weights from source to target.
    Args:
        source (str): Name of the source object.
        target (str): Name of the target object.
    """
    # Get the skin cluster of the source
    source_skin_cluster = mel.eval('findRelatedSkinCluster("%s")' % source)

    if not source_skin_cluster:
        cmds.error("Source object has no skin cluster.")
        return

    # Check if target is already bound
    target_skin_cluster = mel.eval('findRelatedSkinCluster("%s")' % target)
    
    if not target_skin_cluster:
        # Bind the target object to the same joints as the source
        joints = cmds.skinCluster(source_skin_cluster, q=True, inf=True)
        target_skin_cluster = cmds.skinCluster(joints, target, tsb=True)[0]

    # Copy skin weights
    cmds.copySkinWeights(ss=source_skin_cluster, ds=target_skin_cluster, noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='closestJoint')
    cmds.select(target)
    cmds.warning(f"Skin weights copied from {source} to {target}.")

def add_to_source():
    """
    Adds the selected object(s) to the source list (Column A).
    """
    selected = cmds.ls(selection=True)
    if selected:
        existing_items = cmds.textScrollList(source_list, q=True, allItems=True) or []
        for obj in selected:
            if obj not in existing_items:
                cmds.textScrollList(source_list, e=True, append=obj)
    else:
        cmds.warning("No object selected.")

def add_to_target():
    """
    Adds the selected objects to the target list (Column B).
    If a group is selected, it adds all objects in the hierarchy (excluding the group itself).
    """
    selected = cmds.ls(selection=True)
    if selected:
        all_objects_to_add = []

        for obj in selected:
            # Check if the selected object is a transform (group)
            if cmds.objectType(obj) == "transform":
                # Get all child shapes of the group
                children = cmds.listRelatives(obj, allDescendents=True, type="transform")
                if children:
                    all_objects_to_add.extend(children)
                else:
                    all_objects_to_add.append(obj)
            else:
                # Add the object directly if it is not a group
                all_objects_to_add.append(obj)

        # Add objects to the list, ensuring no duplicates
        existing_items = cmds.textScrollList(target_list, q=True, allItems=True) or []
        for obj in all_objects_to_add:
            if obj not in existing_items:
                cmds.textScrollList(target_list, e=True, append=obj)

    else:
        cmds.warning("No object selected.")

def remove_selected_from_source():
    """
    Removes the selected item from the source list (Column A).
    """
    selected_items = cmds.textScrollList(source_list, q=True, selectItem=True)
    if selected_items:
        for item in selected_items:
            cmds.textScrollList(source_list, e=True, removeItem=item)
    else:
        cmds.warning("No item selected in the list.")

def remove_selected_from_target():
    """
    Removes the selected item from the target list (Column B).
    """
    selected_items = cmds.textScrollList(target_list, q=True, selectItem=True)
    if selected_items:
        for item in selected_items:
            cmds.textScrollList(target_list, e=True, removeItem=item)
    else:
        cmds.warning("No item selected in the list.")

def copy_weights_button_pressed():
    """
    Function called when the 'Copy Skin Weights' button is pressed in single source mode.
    """
    source_items = cmds.textScrollList(source_list, q=True, allItems=True)
    target_items = cmds.textScrollList(target_list, q=True, allItems=True)

    if not source_items:
        cmds.warning("Please add a source object to Column A.")
        return
    if not target_items:
        cmds.warning("Please add at least one target object to Column B.")
        return

    source = source_items[0]

    for target in target_items:
        copy_skin_weights(source, target)

def copy_weights_one_to_one():
    """
    Function to copy skin weights from Column A to Column B one-to-one.
    """
    source_items = cmds.textScrollList(source_list, q=True, allItems=True)
    target_items = cmds.textScrollList(target_list, q=True, allItems=True)

    if not source_items:
        cmds.warning("Please add at least one source object to Column A.")
        return
    if not target_items:
        cmds.warning("Please add at least one target object to Column B.")
        return
    if len(source_items) != len(target_items):
        cmds.warning("The number of objects in Column A and Column B must be the same.")
        return

    for source, target in zip(source_items, target_items):
        copy_skin_weights(source, target)

def clear_source_list():
    """
    Clears all items from the source list (Column A).
    """
    cmds.textScrollList(source_list, e=True, removeAll=True)

def clear_target_list():
    """
    Clears all items from the target list (Column B).
    """
    cmds.textScrollList(target_list, e=True, removeAll=True)

def toggle_mode():
    """
    Toggles between single source and multiple source modes.
    """
    current_mode = cmds.button(copy_button, q=True, label=True)
    if current_mode == "Copy Skin Weights (Single Source)":
        cmds.button(copy_button, e=True, label="Copy Skin Weights (One-to-One)", command=lambda x: copy_weights_one_to_one(), backgroundColor=(1.0, 0.6, 0.0))
        cmds.button(toggle_button, e=True, backgroundColor=(1.0, 0.6, 0.0))
        cmds.textScrollList(source_list, e=True, allowMultiSelection=True)
    else:
        cmds.button(copy_button, e=True, label="Copy Skin Weights (Single Source)", command=lambda x: copy_weights_button_pressed(), backgroundColor=(0.4, 0.8, 1.0))
        cmds.button(toggle_button, e=True, backgroundColor=(0.4, 0.8, 1.0))
        cmds.textScrollList(source_list, e=True, allowMultiSelection=False)

def sort_column_a():
    """
    Sorts the items in Column A alphabetically.
    """
    items = cmds.textScrollList(source_list, q=True, allItems=True)
    if items:
        sorted_items = sorted(items)
        cmds.textScrollList(source_list, e=True, removeAll=True)
        for item in sorted_items:
            cmds.textScrollList(source_list, e=True, append=item)

def sort_column_b():
    """
    Sorts the items in Column B alphabetically.
    """
    items = cmds.textScrollList(target_list, q=True, allItems=True)
    if items:
        sorted_items = sorted(items)
        cmds.textScrollList(target_list, e=True, removeAll=True)
        for item in sorted_items:
            cmds.textScrollList(target_list, e=True, append=item)

def create_ui():
    """
    Creates the UI for the tool.
    """
    if cmds.window("copySkinWeightsUI", exists=True):
        cmds.deleteUI("copySkinWeightsUI", window=True)

    window = cmds.window("copySkinWeightsUI", title="Copy Skin Weights Tool", widthHeight=(500, 500))
    cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=10)

    # Toggle mode button at the top
    global toggle_button
    toggle_button = cmds.button(label="Toggle Mode (Single/Multiple Source)", command=lambda x: toggle_mode(), height=40, backgroundColor=(0.4, 0.8, 1.0))

    # Create a row layout with two columns
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth=[(1, 240), (2, 240)], columnAttach=[(1, 'both', 5), (2, 'both', 5)], columnAlign=[(1, 'center'), (2, 'center')])

    # Column A (Source)
    cmds.columnLayout(adjustableColumn=True)
    cmds.frameLayout(label="Source (Column A)", borderStyle="etchedIn")
    global source_list
    source_list = cmds.textScrollList(allowMultiSelection=True, height=200, width=230)
    cmds.button(label="Add Selected to Column A", command=lambda x: add_to_source())
    cmds.button(label="Deselect Selected from Column A", command=lambda x: remove_selected_from_source())
    cmds.button(label="Clear Column A", command=lambda x: clear_source_list())
    cmds.button(label="Sort Column A", command=lambda x: sort_column_a())
    cmds.setParent("..")
    cmds.setParent("..")

    # Column B (Target)
    cmds.columnLayout(adjustableColumn=True)
    cmds.frameLayout(label="Target (Column B)", borderStyle="etchedIn")
    global target_list
    target_list = cmds.textScrollList(allowMultiSelection=True, height=200, width=230)
    cmds.button(label="Add Selected to Column B", command=lambda x: add_to_target())
    cmds.button(label="Deselect Selected from Column B", command=lambda x: remove_selected_from_target())
    cmds.button(label="Clear Column B", command=lambda x: clear_target_list())
    cmds.button(label="Sort Column B", command=lambda x: sort_column_b())
    cmds.setParent("..")
    cmds.setParent("..")

    cmds.setParent("..")  # End rowLayout

    # Control buttons
    cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 5), rowSpacing=10)
    global copy_button
    copy_button = cmds.button(label="Copy Skin Weights (Single Source)", command=lambda x: copy_weights_button_pressed(), height=50, backgroundColor=(0.4, 0.8, 1.0))

    cmds.showWindow(window)

create_ui()