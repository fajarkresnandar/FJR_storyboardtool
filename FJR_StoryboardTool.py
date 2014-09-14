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
#open image and load as sequence strip

import bpy

class FJR_DelAllImage(bpy.types.Operator):
    """Delete all image in active scene"""
    bl_idname = "image.fjr_delallscene"
    bl_label = "del all image "

    def execute(self, context):
        image=bpy.data.images
        for x in image:
            x.user_clear()
        return{'FINISHED'}

class FJR_NuStBoImage(bpy.types.Operator):
    """New image for storyboarding"""
    bl_idname = "image.fjr_nuimage"
    bl_label = "New StoryBoard Image"

    def execute(self, context):
        data= bpy.data
        image= data.images
        scn= bpy.context.scene
        render= scn.render
        
        #fix for blender 269
        scn.sequence_editor_create()
        
        seq = scn.sequence_editor
        sequence = seq.sequences        
        
        x_res= render.resolution_x
        y_res= render.resolution_y
        
        #scene property
        props = context.scene.fjr_stb_tool
        scn_name = props.scene_name
        sht_name = props.shoot_name
        work_dir = props.work_dir
        
        image_name= "scn"+scn_name+"_"+"sh"+sht_name
        
        #check existing image name
        for g in image:
            if g.name ==image_name:
                
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
        seq.active_strip.frame_final_duration=48

        return {'FINISHED'}

class FJR_SbtSaveReload(bpy.types.Operator):
    """New image for storyboarding"""
    bl_idname = "image.fjr_savereaload"
    bl_label = "save and reload "

    def execute(self, context):
        data= bpy.data
        image= data.images
        scn= bpy.context.scene
        render= scn.render        
        
        #bpy.ops.image.save_as()
        
        area=bpy.context.window.screen.areas
        spc =[a for a in area]
        for x in spc :
            if x.spaces.active.type=='IMAGE_EDITOR':
                bpy.ops.image.save()
#            if x.spaces.active.type=='FILE_BROWSER':      
#                bpy.ops.file.refresh()
            if x.spaces.active.type=='SEQUENCE_EDITOR':      
                bpy.ops.sequencer.refresh_all()                
#            else:
#                return{'CANCELLED'}
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
        row.operator("image.fjr_delallscene")
        
        row=layout.row()
        row.label("")        
        
        row=layout.row()
        row.operator("image.external_edit")        
        
        row=layout.row()
        row.operator("image.open")        
        row.operator("image.reload")        
        
class FJR_StoryboardToolProps(bpy.types.PropertyGroup):
    scene_name = bpy.props.StringProperty(
        name='',
        description='scene name for new image',
        default='001',
        options={'SKIP_SAVE'})
    shoot_name = bpy.props.StringProperty(
        name='',
        description='shoot name for new image',
        default='001',
        options={'SKIP_SAVE'})        
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
    
