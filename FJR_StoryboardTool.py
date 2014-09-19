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
    
    
#next task:

#addnu image
##option replace image? if image already there.(report file exist in folder,in sequence,in image editor)
##option use dimension percentage

#delete:active image
## del all image(0), delete squence(1), delete file(0)

#open file:
##auto add image strip 

#paint tool:
##use other image as background(like clone tool)


import bpy
from bpy.props import *

class FJR_DelImage(bpy.types.Operator):
    """Delete all image in active scene"""
    bl_idname = "image.fjr_delimage"
    bl_label = "del image "
    
    delallimage_option = bpy.props.BoolProperty(
        name='delete all image') 

    delimageseq_option = bpy.props.BoolProperty(
        name='delete image sequance') 

    delfileimage_option = bpy.props.BoolProperty(
        name='delete file')     

    def execute(self, context):
        delAllImgOP = self.delallimage_option
        delImgSeqOP = self.delimageseq_option
        delFileImgOP = self.delfileimage_option
        
        image=bpy.data.images
        for x in image:
            x.user_clear()
            image.remove(x)

        spdImg = context.space_data.image
        spdImg.reload()
        context.area.tag_redraw()

        return{'FINISHED'}

    def invoke(self, context, event):
        theBool1 = False
        theBool2 = False
        theBool3 = False 
        #global theFloat, theBool, theString, theEnum
        
        self.delallimage_option = theBool1
        self.delimageseq_option = theBool2
        self.elfileimage_option = theBool3
        return context.window_manager.invoke_props_dialog(self)

class FJR_NuStBoImage(bpy.types.Operator):
    """New image for storyboarding"""
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
        
        
        replaceOP = self.replace_option
        dimensionOP = self.dimension_option
        addSeqOP = self.addsequence_option
        duration = self.seqduration
        
        #fix for blender 269
        scn.sequence_editor_create()
        
        seq = scn.sequence_editor
        sequence = seq.sequences        
        
        x_res= render.resolution_x * render.resolution_percentage /100
        y_res= render.resolution_y * render.resolution_percentage /100
        
        #scene property
        props = context.scene.fjr_stb_tool
        scn_name = str(props.scene_name)
        sht_name = str(props.shoot_name)
        work_dir = props.work_dir
        
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
        
        #check existing image name
        for g in image:
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
        print(startframe)                                        
        
        #auto add image to sequencer
        nu_sequence = sequence.new_image(name=image_name,filepath=file_path,channel=1,frame_start=startframe)
        seq.active_strip = nu_sequence
        seq.active_strip.frame_final_duration=26
        
        bpy.ops.image.fjr_savereaload()
        
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

class FJR_SbtSaveReload(bpy.types.Operator):
    """New image for storyboarding"""
    bl_idname = "image.fjr_savereaload"
    bl_label = "save and reload "

    def execute(self, context):       
        screen = bpy.data.screens
        screenitem = screen.items()
        
        bpy.ops.image.save()
        bpy.ops.sequencer.refresh_all()
        x=bpy.context.window.screen.name
        
        #i don't know how to update screen(in file browser area)
        #this way will not work if only have one screen data

        h = screenitem.index((x,screen[x]))

        if h==0:
            o=h+1
        else:
            o=h-1

        bpy.context.window.screen=screen[o]
        bpy.context.window.screen=screen[h]
        
        #bpy.ops.file.refresh()

        return {'FINISHED'}
        
class FJR_StoryBoardTool_UI(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "FJR_StoryBoardTool"
    bl_idname = "FJR_StoryBoardTool_UI"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        scene = context.scene

        layout = self.layout
        
        row=layout.row()
        row.label(text="scene dir")
        row.prop(context.scene.fjr_stb_tool, 'work_dir')
        
        row=layout.row()
        row.label(text="scene")
        row .prop(context.scene.fjr_stb_tool, 'scene_name')
        
        row=layout.row()
        row.label(text="shoot")
        row.prop(context.scene.fjr_stb_tool, 'shoot_name')        
        
        row=layout.row()
        row.operator("image.fjr_nuimage",text="new image")
        row.operator("image.fjr_savereaload")
        
        row=layout.row()
        row.operator("image.fjr_delimage")
        
        row=layout.row()
        row.label("")        
        
        row=layout.row()
        row.operator("image.external_edit")        
        
        row=layout.row()
        row.operator("image.open")        
        row.operator("image.reload")        
        
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

#(========================
 

#========================)

    work_dir = bpy.props.StringProperty(
        name='',
        description='working directory for storyboarding',
        subtype='DIR_PATH',
        default='//storyboard/',
        options={'SKIP_SAVE'})        
                
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.fjr_stb_tool = bpy.props.PointerProperty(type = FJR_StoryboardToolProps)
        
def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.fjr_stb_tool
    
if __name__ == "__main__":
    register()
    
