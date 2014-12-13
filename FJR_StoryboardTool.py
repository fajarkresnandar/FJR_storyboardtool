bl_info = {
    "name": "FJR_storyboard_tool",
    "author": "Fajar Kresnandar",
    "version": (1, 0),
    "blender": (2, 65, 0),
    "location": "UV/image editor->n properties",
    "description": "automate some process for storyboarding in blender",
    "warning": "make sure you save blend file before creating new image",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Paint"}

import bpy
from bpy.props import *
import os

#reuse function=====================start

def delete_image(x):
    image = bpy.data.images
    x.user_clear()
    image.remove(x)    

def delete_if(x,delImgSeqOPT,delFileImgOPT):
    
    if delFileImgOPT==1:

        file=bpy.path.abspath(x.filepath)
        os.remove(file)
    
    if delImgSeqOPT==1 :
        #check sequence
        CD_sequence(x)        
    return

def CD_sequence(x):
    #check sequence and delete
    scn= bpy.context.scene
    seq = scn.sequence_editor
    sequence = seq.sequences

    strip=[i for i in seq.sequences_all 
            if i.name==x.name]    
    if strip!=[]:                                
        seq.active_strip = seq.sequences_all[x.name]
        sequence.remove(seq.active_strip)

    return

def fjr_reload():
    #i don't know how to update screen(in file browser area)
    #this way will not work if only have one screen data

    screen = bpy.data.screens
    screenitem = screen.items()
    x=bpy.context.window.screen.name
    h = screenitem.index((x,screen[x]))

    if h==0:
        o=h+1
    else:
        o=h-1

    bpy.context.window.screen=screen[o]
    bpy.context.window.screen=screen[h]
    
    return

#reuse function=====================end

#operator=====================start
class FJR_ReloadImage(bpy.types.Operator):
    """Reload image in active image editor, sequence editor & file browser"""
    bl_idname = "image.fjr_reloadimage"
    bl_label = "reload "

    @classmethod
    def poll(self, context):
        return context.area.type == 'IMAGE_EDITOR'    

    def execute(self, context):
        image = bpy.data.images
        
        #refresh only storyboard
        stb=[i for i in image
                if i.name.startswith('scn')]
        for i in stb:
            i.reload()
            
        bpy.ops.image.reload()
        bpy.ops.sequencer.refresh_all()
        fjr_reload()
        
        return{'FINISHED'}

class FJR_DelImage(bpy.types.Operator):
    """Delete image in active scene"""
    bl_idname = "image.fjr_delimage"
    bl_label = "del image "
    
    delallimage_option = bpy.props.BoolProperty(
        name='delete all image') 

    delimageseq_option = bpy.props.BoolProperty(
        name='delete image sequance') 

    delfileimage_option = bpy.props.BoolProperty(
        name='delete file')     

    @classmethod
    def poll(self, context):
        return context.area.type == 'IMAGE_EDITOR'
    
    def execute(self, context):
        #scene properties
        delAllImgOPT = self.delallimage_option
        delImgSeqOPT = self.delimageseq_option
        delFileImgOPT = self.delfileimage_option

        area = bpy.context.area
        space = area.spaces
        image = bpy.data.images            
        
        #delete image    
        if delAllImgOPT==1:
            for x in image:
                delete_if(x,delImgSeqOPT,delFileImgOPT)
                delete_image(x)
            
        if delAllImgOPT==0 :
            #delete active strip
            x=space[0].image
            delete_if(x,delImgSeqOPT,delFileImgOPT)
            
            delete_image(x)
                        
        fjr_reload()
        print('del image')    
#        spdImg = context.space_data.image
#        spdImg.reload()
#        context.area.tag_redraw()
            
        return{'FINISHED'}

    def invoke(self, context, event):
        theBool1 = False
        theBool2 = True
        theBool3 = False 
        #global theFloat, theBool, theString, theEnum
        
        self.delallimage_option = theBool1
        self.delimageseq_option = theBool2
        self.elfileimage_option = theBool3
        return context.window_manager.invoke_props_dialog(self)

class FJR_NuStBoImage(bpy.types.Operator):
    """Create new storyboard image"""
    bl_idname = "image.fjr_nuimage"
    bl_label = "New StoryBoard Image"
    
    replace_option  = BoolProperty(name="replace image")
    dimension_option = BoolProperty(name="use dimension")
    addsequence_option = bpy.props.BoolProperty(name='add sequence')
    seqduration = bpy.props.IntProperty(name='sequence duration')
    
    def execute(self, context):
        data= bpy.data
        image= data.images
        scn= bpy.context.scene
        render= scn.render
        
        #scene property
        props = context.scene.fjr_stb_tool
        work_dir = props.work_dir
        scn_name = str(props.scene_name)
        sht_name = str(props.shoot_name)
        prvix_name = props.previx
        prvix_opt = props.opt_previx
        
        replaceOPT = self.replace_option
        dimensionOPT = self.dimension_option
        addSeqOPT = self.addsequence_option
        duration = self.seqduration
        
        #fix for blender 269
        scn.sequence_editor_create()
        
        seq = scn.sequence_editor
        sequence = seq.sequences        
        
        x_res= render.resolution_x
        y_res= render.resolution_y
                
        #use dimension
        if dimensionOPT==1: 
            x_res= render.resolution_x * render.resolution_percentage /100
            y_res= render.resolution_y * render.resolution_percentage /100
        
        #count string
        sc=len(scn_name)
        sh=len(sht_name)
        
        #add prefix
        if sc==1:
            scn_name='00'+scn_name
        if sc==2:
            scn_name='0'+scn_name
        
        if sh==1:
            sht_name='00'+sht_name
        if sh==2:
            sht_name='0'+sht_name
        
        image_name= "scn"+scn_name+"_"+"sh"+sht_name
        if prvix_opt==1:
            image_name= "scn"+scn_name+"_"+"sh"+sht_name+"_"+prvix_name

        if replaceOPT==1:
            #bpy.ops.image.fjr_delimage()
            x=image[image_name]
            CD_sequence(x)            
            delete_image(x)
            
        if replaceOPT==0:
            for g in image:
                #check existing image name
                if g.name ==image_name:
                    self.report({"ERROR"}, "File %s sudah ada." % image_name)
                    return{'CANCELLED'}

        #create new image and save in work directory
        bpy.ops.image.new(name=image_name, width=x_res, height=y_res, color=(1, 1, 1, 1), alpha=True, generated_type='BLANK', float=False)        
        
        file_format = bpy.context.space_data.image.file_format
                
        format= file_format.lower()
        file_path = work_dir+"/"+image_name+"."+format
        img_file = image_name+"."+ file_format
        
#        bpy.context.space_data.active.image.file_format
#        bpy.context.window.screen.areas[2].spaces.active.image.file_format
#        bpy.context.window.screen.areas[1].spaces.active.
        
        #auto save image
        bpy.ops.image.save_as(save_as_render=False, copy=False, filepath=file_path,\
        check_existing=True, filter_blender=False, filter_backup=False, filter_image=True,\
        filter_movie=True, filter_python=False, filter_font=False, filter_sound=False,\
        filter_text=False, filter_btx=False, filter_collada=False, filter_folder=True, \
        filemode=9, relative_path=True, display_type='FILE_DEFAULTDISPLAY')
        
        image[image_name].use_fake_user=1

        #get sequence start position
        all_seq = seq.sequences_all
        str_1 = [a for a in all_seq
                    if a.channel==1]        
        startframe= 1        
        for x in str_1:
            seq.active_strip = x
            activestart= x.frame_start
            if activestart >= startframe:
                startframe=activestart+x.frame_final_duration
        #print(startframe)                                        
        
        #auto add image to sequencer
        if addSeqOPT==1:
            nu_sequence = sequence.new_image(name=image_name,filepath=file_path,channel=1,frame_start=startframe)
            seq.active_strip = nu_sequence
            seq.active_strip.frame_final_duration=duration
        
        bpy.ops.image.fjr_save_edit()
        
        return {'FINISHED'}

    def invoke(self, context, event):
        theBool1 = False
        theBool2 = True
        theBool3 = True
        theInt1 = 26
        #global theFloat, theBool, theString, theEnum
        
        self.replace_option = theBool1
        self.dimension_option = theBool2
        self.addsequence_option = theBool3
        self.seqduration = theInt1
                
        return context.window_manager.invoke_props_dialog(self)

class FJR_StbSaveEdit(bpy.types.Operator):
    """Save image in image in image editor, reload image in file editor and sequence editor """

    bl_idname = "image.fjr_save_edit"
    bl_label = "save edit"

    def execute(self, context):       
        
        bpy.ops.image.save()
        bpy.ops.sequencer.refresh_all()
        fjr_reload()        
        return {'FINISHED'}

#nafigation=========================start

def find_id(list, name):
    """return id from list"""
    id=0
    for l in list:
        if l != name:
            id=id+1
        else :
            break
    return id

def nextImg_id(next,list,id_crnt):
    """return next image id from image list"""
    
    allId_list = len(list)-1
    if next=="next":
        id_next = id_crnt+1
        if id_next > allId_list:
            id_next = 0
    if next=="prev":
        id_next = id_crnt-1
        if id_next==-1:
            id_next = allId_list
            
    return id_next
    
class FJR_Image_Next(bpy.types.Operator):
    """Next image in image editor """
    bl_idname = "image.fjr_nextimage"
    bl_label = "next"

    @classmethod
    def poll(self, context):
        return context.area.type == 'IMAGE_EDITOR'    

    def execute(self, context):
        data = bpy.data
        image = data.images
        
        prop = bpy.context.scene.fjr_stb_tool
        use_all = prop.opt_nav_all_img
        
        area = context.area
        space = area.spaces[0].image
        
        if use_all==1:
            id_actvImg=image.find(space.name)
            id_next = nextImg_id("next",image,id_actvImg)
            
            area.spaces[0].image= image[id_next]
            
        else :
            img_list=[m.name for m in image
                        if m.name.startswith("scn")]
            id_actvImg = find_id(img_list, space.name)
            id_next = nextImg_id("next",img_list, id_actvImg)
            
            area.spaces[0].image= image[img_list[id_next]]
        
        return{'FINISHED'}

class FJR_Image_Prev(bpy.types.Operator):
    """Previous image in image editor """
    bl_idname = "image.fjr_previmage"
    bl_label = "pref"

    @classmethod
    def poll(self, context):
        return context.area.type == 'IMAGE_EDITOR'    

    def execute(self, context):
        data=bpy.data
        image= data.images

        prop = bpy.context.scene.fjr_stb_tool
        use_all = prop.opt_nav_all_img
        
        area = context.area
        space = area.spaces[0].image
        
        if use_all==1:
            id_actvImg=image.find(space.name)            
            id_next=nextImg_id("prev",image,id_actvImg)
            area.spaces[0].image= image[id_next]
            
        else:
            img_list=[m.name for m in image
                        if m.name.startswith("scn")]
            id_actvImg = find_id(img_list, space.name)
            id_next = nextImg_id("prev",img_list, id_actvImg)
            
            area.spaces[0].image= image[img_list[id_next]]
        
        return{'FINISHED'}

class FJR_Image_Frist(bpy.types.Operator):
    """First image in image editor """
    bl_idname = "image.fjr_firstimage"
    bl_label = "first_image"

    @classmethod
    def poll(self, context):
        return context.area.type == 'IMAGE_EDITOR'    

    def execute(self, context):
        data=bpy.data
        image= data.images
        area = context.area
        space = area.spaces[0].image

        prop = bpy.context.scene.fjr_stb_tool
        use_all = prop.opt_nav_all_img        
        
        if use_all==1:
            area.spaces[0].image= image[0]
        else:
            img_list=[m.name for m in image
                        if m.name.startswith("scn")]
            area.spaces[0].image= image[img_list[0]]
            
        return{'FINISHED'}

class FJR_Image_Last(bpy.types.Operator):
    """Last image in image editor """
    bl_idname = "image.fjr_lastimage"
    bl_label = "last_image"

    @classmethod
    def poll(self, context):
        return context.area.type == 'IMAGE_EDITOR'    

    def execute(self, context):
        data=bpy.data
        image= data.images
        area = context.area
        space = area.spaces[0].image
        
        prop = bpy.context.scene.fjr_stb_tool
        use_all = prop.opt_nav_all_img          

        if use_all==1:
            allId_list = len (image)-1
            area.spaces[0].image= image[allId_list]
        else:            
            img_list=[m.name for m in image
                        if m.name.startswith("scn")]
            allId_list = len (img_list)-1
            area.spaces[0].image= image[img_list[allId_list]]
        
        return{'FINISHED'}

#nafigation=========================end

def FJR_move(id_crnt, id_next, list_allid_stb, list_id_chng, id_last_chng, direction):
    """move image to id_next"""

    data = bpy.data
    image = data.images
    area = bpy.context.area
    space = area.spaces[0].image
    
    #add more image to the change_list
    if direction == 'right':
        if id_last_chng < list_allid_stb[len(list_allid_stb)-1]:
            list_id_chng.extend([id_next])
            id_last_chng = id_next
            id_next=list_id_chng[0]
    if direction == 'left':
        if id_last_chng > list_allid_stb[0] :
            list_id_chng.extend([id_next])
            list_id_chng=sorted(list_id_chng)
            id_last_chng = id_next
            id_next= list_id_chng[len(list_id_chng)-1]
    
    for i in list_id_chng:
        next=i+1
        if direction == 'left':
            next = i-1
            
        if i != id_last_chng:
            #get image path for i
            filepath_crnt = bpy.path.abspath(image[i].filepath)
            filename_crnt = bpy.path.basename(filepath_crnt)
            path_crnt = filepath_crnt.replace(filename_crnt,"")
            
            #get next image path
            filepath_next=bpy.path.abspath(image[next].filepath)
            filename_next=bpy.path.basename(filepath_next)
            path_next=filepath_next.replace(filename_next,"")
            
            #rename imagepath
            nu_filepath_crnt = path_crnt+'pre_'+filename_next        
            os.rename(filepath_crnt, nu_filepath_crnt)
            
            #nuCrnt_img_file = bpy.path.basename(nu_filepath_crnt)
            #nupath_crnt = nu_filepath_current.replace(nuCrnt_img_file,"")
            
        if i == id_last_chng:
            #get image path for i
            filepath_crnt = bpy.path.abspath(image[i].filepath)
            filename_crnt = bpy.path.basename(filepath_crnt)
            path_crnt = filepath_crnt.replace(filename_crnt,"")
            
            #get next image path
            filepath_next = bpy.path.abspath(image[id_next].filepath)
            filename_next = bpy.path.basename(filepath_next)
            path_next = filepath_next.replace(filename_next,"")
            
            #rename imagepath
            nu_filepath_crnt = path_crnt+'pre_'+filename_next
            os.rename(filepath_crnt, nu_filepath_crnt)
            
            #nuCrnt_img_file = bpy.path.basename(nu_filepath_crnt)
            #nupath_crnt = nu_filepath_current.replace(nuCrnt_img_file,"")
    
    #rename it again (delete frefix 'pre')
    for i in list_id_chng:
        #get image path for i
        
        filepath_i = bpy.path.abspath(image[i].filepath)
        filename_i =bpy.path.basename(filepath_i)
        
        path_i = filepath_i.replace(filename_i,"")
        
        filename_pre = 'pre_'+ filename_i
        filepath_pre = path_i + filename_pre
       
        os.rename(filepath_pre , filepath_i)
    
    bpy.ops.image.fjr_reloadimage()
    
    return
    
class FJR_Move_Next(bpy.types.Operator):
    """Move image to the next """
    bl_idname = "image.fjr_movenext"
    bl_label = "move_next"

    @classmethod
    def poll(self, context):
        return context.area.type == 'IMAGE_EDITOR' 
    
    def execute(self, context):
        
        direction='right'
        data=bpy.data
        image= data.images
        area = context.area
        space = area.spaces[0].image
        
        props = context.scene.fjr_stb_tool
        incld_right = props.opt_include_right
        incld_left = props.opt_include_left
        
        #return cenceled if current image not start with "scn"
        if not space.name.startswith("scn"):
            return {'CANCELLED'}

        #id active image and next image
        #sort id of stb image (in image list)
        list_allid_stb=[image.find(i.name) for i in image
                            if i.name.startswith('scn')]
        id_last_stb = list_allid_stb[len(list_allid_stb)-1]

#        len_allId =len(list_allid_stb)
        id_crnt = image.find(space.name)

        #create id list for files want tobe change
        crnt_list=[id_crnt] #current file
        r_chng_list=[] #file @right
        l_chng_list=[] #file @left
        if incld_right ==1 :
            for i in list_allid_stb:
                if i > id_crnt:
                    r_chng_list.extend([i])
                
        if incld_left ==1 :
            for i in list_allid_stb:
                if i < id_crnt:
                    l_chng_list.extend([i])
        
        #marge id list
        list_id_chng = sorted(crnt_list + r_chng_list + l_chng_list)
        id_last_chng = list_id_chng[len(list_id_chng)-1]
        
        #define next id/ turn point for last id
        if id_last_chng < id_last_stb:
            id_next = id_crnt+1 
        if id_last_chng == id_last_stb:
            id_next = list_id_chng[0]
        if len(list_id_chng)==1 and id_crnt == id_last_stb :
            id_next = list_allid_stb[0]
            list_id_chng = list_allid_stb
        
        FJR_move(id_crnt, id_next, list_allid_stb, list_id_chng, id_last_chng,direction)
        
#        bpy.ops.image.fjr_nextimage()

        return{'FINISHED'}

class FJR_Move_Prev(bpy.types.Operator):
    """Move image to the previous """
    bl_idname = "image.fjr_moveprev"
    bl_label = "move_prev"

    @classmethod
    def poll(self, context):
        return context.area.type == 'IMAGE_EDITOR'
    def execute(self, context):
        direction='left'
        data=bpy.data
        image= data.images
        area = context.area
        space = area.spaces[0].image
        
        props = context.scene.fjr_stb_tool
        incld_right = props.opt_include_right
        incld_left = props.opt_include_left
        
        #return cenceled if current image not start with "scn"
        if not space.name.startswith("scn"):
            return {'CANCELLED'}
        
        #sort id of stb image (in image list)
        list_allid_stb=[image.find(i.name) for i in image
                            if i.name.startswith('scn')]
        id_last_stb = list_allid_stb[0]        
        
        #len_allId =len(list_allid_stb)
        id_crnt = image.find(space.name)
        
        #create id list for files want tobe change
        crnt_list=[id_crnt]
        r_chng_list=[]
        l_chng_list=[]
        if incld_right ==1 :
            for i in list_allid_stb:
                if i > id_crnt:
                    r_chng_list.extend([i])
                
        if incld_left ==1 :
            for i in list_allid_stb:
                if i < id_crnt:
                    l_chng_list.extend([i])
        
        #marge id list
        list_id_chng= sorted(crnt_list+ r_chng_list + l_chng_list)
        id_last_chng = list_id_chng[0]
        
        #define next id/ turn point for last id
        if id_last_chng == id_last_stb:
            id_next = list_id_chng[len(list_id_chng)-1]
        if id_last_chng > id_last_stb:
            id_next = id_crnt-1 
        if len(list_id_chng)==1 and id_crnt == id_last_stb :
            id_next = list_allid_stb[len(list_allid_stb)-1]
            list_id_chng = list_allid_stb    
       
        FJR_move(id_crnt, id_next, list_allid_stb, list_id_chng, id_last_chng,direction)

        #bpy.ops.image.fjr_previmage()        
                        
        return{'FINISHED'}
    
#operator=====================end

class FJR_StoryBoardTool_File_UI(bpy.types.Panel):
    """Creates a Panel in file browser"""
    bl_label = "FJR_StoryBoardTool_Rearrange"
    bl_idname = "Rearrange_Image"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        scene = context.scene
        props = scene.fjr_stb_tool
        layout = self.layout
        
        row=layout.row(align=True)
        row.alignment = 'CENTER'
        row.prop(props, 'opt_include_left',text='')
        row.operator("image.fjr_moveprev",icon='TRIA_LEFT',text='')
        row.operator("image.fjr_movenext",icon='TRIA_RIGHT',text='')
        row.prop(props, 'opt_include_right',text='')

class FJR_StoryBoardTool_UI(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "FJR_StoryBoardTool"
    bl_idname = "FJR_StoryBoardTool_UI"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        scene = context.scene
        props = scene.fjr_stb_tool
        use_previx = props.opt_previx
        
        layout = self.layout

        box=layout.box()
        
        row=box.row()
        row.prop(props, 'work_dir')
        
        row=box.row()
        col=row.column()
        col .prop(props, 'scene_name',text="scene ")
        col.prop(props, 'shoot_name',text="shoot ")
        
        col=row.column()
        col.scale_y=2
        col.operator("image.fjr_nuimage",text="new image")
        
        row=box.row()
        row.prop(props, 'opt_previx',text="use previx")
        if use_previx==1:
            row.prop(props,'previx')
              
        row=layout.row()
        row.operator("image.fjr_delimage",icon='CANCEL')
        row.operator("image.fjr_save_edit")
        
        row=layout.row(align=True)
        row.operator("image.fjr_reloadimage",icon='FILE_REFRESH')        
        row.operator("image.external_edit",text='edit external')        
        
#        row=layout.row()
#        row.operator("image.open",icon='FILE_FOLDER')        
        
        split = layout.split(percentage= 0.5)
        row=split.row(align=True)
        #row=layout.row(align=True)
        row.prop(props, 'opt_nav_all_img',text='use all')
        
        row=split.row(align=True)
        row.alignment = 'CENTER'
        row.operator("image.fjr_firstimage",icon='REW',text='')
        row.operator("image.fjr_previmage",icon='TRIA_LEFT',text='')        
        row.operator("image.fjr_nextimage",icon='TRIA_RIGHT',text='')
        row.operator("image.fjr_lastimage",icon='FF',text='')
        

class FJR_StoryboardToolProps(bpy.types.PropertyGroup):
    scene_name = bpy.props.IntProperty(
        name='',
        description='scene name for new image',
        default=0,
        min=0,
        max=100,
        step=1,        
        options={'SKIP_SAVE'})

    shoot_name = bpy.props.IntProperty(
        name='',
        description='shoot name for new image',
        default=0,
        min=0,
        max=100,
        step=1,        
        options={'SKIP_SAVE'})

    work_dir = bpy.props.StringProperty(
        name='',
        description='Directory/name to save new storyboard image',
        subtype='DIR_PATH',
        default='//storyboard/',
        options={'SKIP_SAVE'})        
                
    opt_previx = bpy.props.BoolProperty(
        name='',
        default=0,
        description='option use previx',
        options={'SKIP_SAVE'})        

    previx = bpy.props.StringProperty(
        name='',
        description='prefix',
        default="",
        options={'SKIP_SAVE'})

    opt_include_right = bpy.props.BoolProperty(
        name='',
        default=0,
        description='option include all right image when move image',
        options={'SKIP_SAVE'})        

    opt_include_left = bpy.props.BoolProperty(
        name='',
        default=0,
        description='option include all left image when move image',
        options={'SKIP_SAVE'})

    opt_nav_all_img = bpy.props.BoolProperty(
        name='',
        default=0,
        description='option include all image, not only storyboard image',
        options={'SKIP_SAVE'})         

#def imgedit_header_navigate(self, context):
#    layout=self.layout
#    row=layout.row(align=True)
#    row.label(text='  ')
#    row.operator("image.fjr_firstimage",icon='REW',text='')
#    row.operator("image.fjr_previmage",icon='TRIA_LEFT',text='')        
#    row.operator("image.fjr_nextimage",icon='TRIA_RIGHT',text='')
#    row.operator("image.fjr_lastimage",icon='FF',text='')    

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.fjr_stb_tool = bpy.props.PointerProperty(type = FJR_StoryboardToolProps)
#    bpy.types.IMAGE_HT_header.append(imgedit_header_navigate)
        
def unregister():
    bpy.utils.unregister_module(__name__)
#    bpy.types.IMAGE_HT_header.remove(imgedit_header_navigate)

    del bpy.types.Scene.fjr_stb_tool
    
if __name__ == "__main__":
    register()
