import arcpy
import ctypes

Message = arcpy.GetParameterAsText(0)
Title = arcpy.GetParameterAsText(1)


def x (Message, Title):
  MessageBox = ctypes.windll.user32.MessageBoxA
  returnValue = MessageBox( 0, Message, Title, 0x00040000L | 0x00000003L )
  return returnValue

x("You are now ready to do THIS or THAT", "What's Next?")