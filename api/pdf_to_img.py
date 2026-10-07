#!/usr/bin/env python
# coding: utf-8

# # PDF to IMG

# In[1]:


import math
import sys
import ctypes
import os.path
import PIL.Image
import pypdfium2.raw as pdfium_c


# # Read Parameter

# In[2]:


#Vérification de la présence de un paramètre (Exit si pas respecté)
if len(sys.argv) != 2:
    print("Usage: python pdf_to_img.py <nom_document.pdf>")
    sys.exit(1)

#Récupération des valeurs des deux paramètres
param1 = sys.argv[1]
#param1 = "docu.pdf"
param1_out = param1.replace(".pdf",".png")


# # Load the document

# In[3]:


#Chargement du document
filepath = os.path.abspath(param1)
pdf = pdfium_c.FPDF_LoadDocument((filepath+"\x00").encode("utf-8"), None)


# # Check page count to make sure it was loaded correctly

# In[4]:


#Verification du nombre de page du document
page_count = pdfium_c.FPDF_GetPageCount(pdf)
assert page_count >= 1


# # Load the first page and get its dimensions

# In[5]:


#Charge la page et retient les dimensions
page = pdfium_c.FPDF_LoadPage(pdf, 0)
width  = math.ceil(pdfium_c.FPDF_GetPageWidthF(page))
height = math.ceil(pdfium_c.FPDF_GetPageHeightF(page))


# # Create a bitmap
# # (Note, pdfium is faster at rendering transparency if we use BGRA rather than BGRx)

# In[6]:


#Enregistre les informations pour le rendu de l'image
use_alpha = pdfium_c.FPDFPage_HasTransparency(page)
bitmap = pdfium_c.FPDFBitmap_Create(width, height, int(use_alpha))


# # Fill the whole bitmap with a white background
# # The color is given as a 32-bit integer in ARGB format (8 bits per channel)

# In[7]:


#Stock les arguments du rendu
pdfium_c.FPDFBitmap_FillRect(bitmap, 0, 0, width, height, 0xFFFFFFFF)


# In[9]:


render_args = (
    bitmap,  # the bitmap
    page,    # the page
    # positions and sizes are to be given in pixels and may exceed the bitmap
    0,       # left start position
    0,       # top start position
    width,   # horizontal size
    height,  # vertical size
    0,       # rotation (as constant, not in degrees!)
    pdfium_c.FPDF_LCD_TEXT | pdfium_c.FPDF_ANNOT,  # rendering flags, combined with binary or
)


# # Render the page

# In[10]:


#Rendu de la page
pdfium_c.FPDF_RenderPageBitmap(*render_args)


# # Get a pointer to the first item of the buffer

# In[11]:


#Curseur sur le premier objet de la bitmap
buffer_ptr = pdfium_c.FPDFBitmap_GetBuffer(bitmap)


# # Re-interpret the pointer to encompass the whole buffer

# In[12]:


#Deplace le curseur pour reproduire l'intégralité de l'image
buffer_ptr = ctypes.cast(buffer_ptr, ctypes.POINTER(ctypes.c_ubyte * (width * height * 4)))


# # Create a PIL image from the buffer contents

# In[13]:


#Création de l'image
img = PIL.Image.frombuffer("RGBA", (width, height), buffer_ptr.contents, "raw", "BGRA", 0, 1)


# # Save it as file

# In[14]:


#Sauvegarde de l'image
img.save(param1_out)

