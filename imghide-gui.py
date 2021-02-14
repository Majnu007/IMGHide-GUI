import tkinter as tk
from tkinter import messagebox
import PIL.Image
import PIL.ImageTk
from PIL import Image
import os.path
from os import path
import math
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
import base64
import os
from sys import exit
from random import choice

window = tk.Tk()
window.title('IMGHide GUI v1.0')
window.geometry('550x370')
window.configure(bg='deepskyblue4')
window.minsize(550, 370)
window.maxsize(550, 370)

im1 = PIL.Image.open(choice(["assets/header.png", "assets/header2.png"]))
header = PIL.ImageTk.PhotoImage(im1)

im2 = PIL.Image.open("assets/enc_button.png")
enc_button = PIL.ImageTk.PhotoImage(im2)

im3 = PIL.Image.open("assets/dec_button.png")
dec_button = PIL.ImageTk.PhotoImage(im3)


def encrypt(key, source, encode=True):
    key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = Random.new().read(AES.block_size)  # generate IV
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size  # calculate needed padding
    source += bytes([padding]) * padding  # Python 2.x: source += chr(padding) * padding
    data = IV + encryptor.encrypt(source)  # store the IV at the beginning and encrypt
    return base64.b64encode(data).decode() if encode else data

def decrypt(key, source, decode=True):
    if decode:
        source = base64.b64decode(source.encode())
    key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = source[:AES.block_size]  # extract the IV from the beginning
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:])  # decrypt
    padding = data[-1]  # pick the padding value from the end; Python 2.x: ord(data[-1])
    if data[-padding:] != bytes([padding]) * padding:  # Python 2.x: chr(padding) * padding
        messagebox.showerror("Error", "Invalid Padding Detected When Decrypting The Message !!!")
    return data[:-padding]  # remove the padding

def convertToRGB(img):
    try:
        rgba_image = img
        rgba_image.load()
        background = Image.new("RGB", rgba_image.size, (255, 255, 255))
        background.paste(rgba_image, mask = rgba_image.split()[3])
        info_label.config(text='$ Converted image to RGB')
        return background
    except Exception as e:
        info_label.config(text="$ Couldn't convert image to RGB")
        messagebox.showerror("Error", f"Couldn't convert image to RGB\n{e}")
        exit(1)

def getPixelCount(img):
    width, height = Image.open(img).size
    return width*height

def encodeImage(image,message,filename):
    info_label.config(text="$ Encoding The Image")
    try:
        width, height = image.size
        pix = image.getdata()

        current_pixel = 0
        tmp=0
        # three_pixels = []
        x=0
        y=0

        info_label.config(text="$ Encoding The Image.")

        for ch in message:
            info_label.config(text="$ Encoding The Image..")
            binary_value = format(ord(ch), '08b')
            # For each character, get 3 pixels at a time
            p1 = pix[current_pixel]
            p2 = pix[current_pixel+1]
            p3 = pix[current_pixel+2]

            three_pixels = [val for val in p1+p2+p3]
            for i in range(0,8):
                current_bit = binary_value[i]
            
                if current_bit == '0':
                    if three_pixels[i]%2!=0:
                        three_pixels[i]= three_pixels[i]-1 if three_pixels[i]==255 else three_pixels[i]+1
                elif current_bit == '1':
                    if three_pixels[i]%2==0:
                        three_pixels[i]= three_pixels[i]-1 if three_pixels[i]==255 else three_pixels[i]+1

            current_pixel+=3
            tmp+=1

            #Set 9th value
            if(tmp==len(message)):
                # Make as 1 (odd) - stop reading
                if three_pixels[-1]%2==0:
                    three_pixels[-1]= three_pixels[-1]-1 if three_pixels[-1]==255 else three_pixels[-1]+1
            else:
                # Make as 0 (even) - continue reading
                if three_pixels[-1]%2!=0:
                    three_pixels[-1]= three_pixels[-1]-1 if three_pixels[-1]==255 else three_pixels[-1]+1

            three_pixels = tuple(three_pixels)
                
            st=0
            end=3
            for i in range(0,3):
                image.putpixel((x,y), three_pixels[st:end])
                st+=3
                end+=3

                if (x == width - 1):
                    x = 0
                    y += 1
                else:
                    x += 1

            info_label.config(text="$ Encoding The Image...")

        encoded_filename = filename.split('.')[0] + "-enc.png"
        image.save(encoded_filename)
        info_label.config(text="$ Image Saved Successfully")
        messagebox.showinfo("Success", f"Image encoded and saved as {encoded_filename}\nOriginal filename {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occured\n{e}")
        exit(1)

def decodeImage(image):
    info_label.config(text="$ Decoding The Image")
    try:
        pix = image.getdata()
        current_pixel = 0
        decoded=""

        info_label.config(text="$ Decoding The Image.")
        while True:
            info_label.config(text="$ Decoding The Image..")
            # Get 3 pixels each time
            binary_value=""
            p1 = pix[current_pixel]
            p2 = pix[current_pixel+1]
            p3 = pix[current_pixel+2]
            three_pixels = [val for val in p1+p2+p3]

            for i in range(0,8):
                if three_pixels[i]%2==0:
                    binary_value+="0"
                elif three_pixels[i]%2!=0:
                    binary_value+="1"

            info_label.config(text="$ Decoding The Image...")

            #Convert binary value to ascii and add to string
            binary_value.strip()
            ascii_value = int(binary_value,2)
            decoded+=chr(ascii_value)
            current_pixel+=3
            info_label.config(text="$ Decoding The Image.")

            if three_pixels[-1]%2!=0:
                # stop reading
                break

        info_label.config(text="$ Image Decoded")
        return decoded
    except Exception as e:
        messagebox.showerror("Error", f"An error occured\n{e}")
        exit(1)

def insertHeaders(img):
    pass


def init_encode():
    c2.config(state='disabled')
    encode_button.config(state='disabled')

    img = path_var.get()
    if(not(path.exists(img))):
        messagebox.showerror("Error", "Image not found!\nGiven Image Name/Path is Invalid")
        exit(1)

    message = str(msg_var.get())
    if(len(message)*3 > getPixelCount(img)):
        messagebox.showerror("Error", "Given message is too long to be encoded in the image.\nPlease try another image with more pixels")
        exit(1)

    password = password_var.get()

    cipher=""
    if password!="":
        cipher = encrypt(key=password.encode(),source=message.encode())
    else:
        cipher = message

    image = Image.open(img)
    info_label.config(text=f"Image Mode: {image.mode}")
    if image.mode!='RGB':
        image = convertToRGB(image)
    newimg = image.copy()
    encodeImage(image=newimg,message=cipher,filename=image.filename)
    encode_button.config(state='normal')
    c2.config(state='normal')
    checkbox_var1.set(0)
    checkbox_var2.set(0)
    disable_checkbox()

def copytext(msg):
    r = tk.Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(msg)
    r.update()

def init_decode():
    c1.config(state='disabled')
    encode_button.config(state='disabled')

    img = path_var.get()
    if(not(path.exists(img))):
        messagebox.showerror("Error", "Image not found!\nFilename/Path Provided is Invalid!")
        exit(1)

    password = str(password_var.get())
    image = Image.open(img)
    cipher = decodeImage(image)
    decrypted=""

    if password!="":
        decrypted = decrypt(key=password.encode(), source=cipher)
    else:
        decrypted=cipher

    response = messagebox.askyesno("Decoded Message", f'"{decrypted.decode("UTF-8")}"\n\nDo You Want To Copy The Message ?')
    if response == True:
        copytext(decrypted)

    c1.config(state='normal')
    encode_button.config(state='normal')
    checkbox_var1.set(0)
    checkbox_var2.set(0)
    disable_checkbox()

def disable_checkbox():
    global path_entry, msg_entry, password_entry, encode_button, label1, label2, label3, label4

    if (checkbox_var1.get() == 1) & (checkbox_var2.get() == 0):
        info_label.config(text='$ Encode Selected')
        c2.config(state='disabled')

        label1 = tk.Label(window,bg='deepskyblue4',fg='white', text='File Name/Path', font=('calibre',9,'normal'))
        label1.place(relx = 0.3, rely = 0.43, anchor = 'center')
        path_entry = tk.Entry(window,textvariable = path_var, font=('calibre',10,'normal'))
        path_entry.place(relx = 0.4, rely = 0.43, anchor = 'w')

        label2 = tk.Label(window,bg='deepskyblue4',fg='white', text=' Message', font=('calibre',9,'normal'))
        label2.place(relx = 0.33, rely = 0.53, anchor = 'center')
        msg_entry = tk.Entry(window,textvariable = msg_var, font=('calibre',10,'normal'))
        msg_entry.place(relx = 0.4, rely = 0.53, anchor = 'w')

        label3 = tk.Label(window,bg='deepskyblue4',fg='white', text='Password', font=('calibre',9,'normal'))
        label3.place(relx = 0.33, rely = 0.63, anchor = 'center')
        password_entry = tk.Entry(window,textvariable = password_var, font=('calibre',10,'normal'))
        password_entry.place(relx = 0.4, rely = 0.63, anchor = 'w')
        label4 = tk.Label(window,bg='deepskyblue4',fg='white',text='(Leave Empty For No Password)', font=('calibre',9,'normal'))
        label4.place(relx = 0.5, rely = 0.7, anchor = 'center')

#        encode_button = tk.Button(window,bg='lawngreen',text='Encode!',borderwidth = 4,relief="flat",command=init_encode)
        encode_button = tk.Button(window,image=enc_button,borderwidth = 2,relief="flat",command=init_encode)
        encode_button.place(relx = 0.4, rely = 0.825, anchor = 'w')

    elif (checkbox_var1.get() == 0) & (checkbox_var2.get() == 1):
        info_label.config(text='$ Decode Selected')
        c1.config(state='disabled')

        label1 = tk.Label(window,bg='deepskyblue4',fg='white', text='File Name/Path', font=('calibre',9,'normal'))
        label1.place(relx = 0.3, rely = 0.45, anchor = 'center')
        path_entry = tk.Entry(window,textvariable = path_var, font=('calibre',10,'normal'))
        path_entry.place(relx = 0.4, rely = 0.45, anchor = 'w')

        label2 = tk.Label(window,bg='deepskyblue4',fg='white', text='Password', font=('calibre',9,'normal'))
        label2.place(relx = 0.33, rely = 0.55, anchor = 'center')

        label3 = tk.Label(window, text='', font=('calibre',9,'normal'))
        password_entry = tk.Entry(window,textvariable=password_var, font=('calibre',10,'normal'))
        password_entry.place(relx = 0.4, rely = 0.55, anchor = 'w')

        label4 = tk.Label(window,bg='deepskyblue4',fg='white', text='(Leave Empty For No Password)', font=('calibre',9,'normal'))
        label4.place(relx = 0.5, rely = 0.65, anchor = 'center')

        msg_entry = tk.Entry(window,textvariable = msg_var, font=('calibre',10,'normal'))

#        encode_button = tk.Button(window,bg='skyblue',command=init_decode,borderwidth = 4,relief="flat",text='Decode!')
        encode_button = tk.Button(window,image=dec_button,command=init_decode,borderwidth = 2,relief="flat")
        encode_button.place(relx = 0.4, rely = 0.8, anchor = 'w')

    elif (checkbox_var1.get() == 0) & (checkbox_var2.get() == 0):
        info_label.config(text='$ Nothing Selected')
        c1.config(state='normal')
        c2.config(state='normal')
        path_entry.destroy()
        msg_entry.destroy()
        password_entry.destroy()
        encode_button.destroy()
        label1.destroy()
        label2.destroy()
        label3.destroy()
        label4.destroy()
    else:
        info_label.config(text='$ Selected Nothing')

checkbox_var1 = tk.IntVar()
checkbox_var2 = tk.IntVar()
path_var = tk.StringVar()
password_var = tk.StringVar()
msg_var = tk.StringVar()

#title = tk.Label(window, text='IMGHide GUI v1.0', font=('TkHeadingFont',35,'bold','underline'))
title = tk.Label(window, image=header, bg='deepskyblue4')
title.place(relx = 0.5, rely = 0.12, anchor = 'center')

c1 = tk.Checkbutton(window, text='Encode', bg='skyblue', variable=checkbox_var1, onvalue=1, offvalue=0, command=disable_checkbox)
c1.place(relx = 0.5, rely = 0.28, anchor = 'center')

c2 = tk.Checkbutton(window,text='Decode', bg='lawngreen', variable=checkbox_var2, onvalue=1, offvalue=0, command=disable_checkbox)
c2.place(relx = 0.5, rely = 0.35, anchor = 'center')

info_label = tk.Label(window, bg='black', fg='lawngreen',width=30, text='$ Everything Initialised', font=('calibre',9,'normal'))
info_label.place(relx = 0.0, rely = 1.0, anchor ='sw')

author_label = tk.Label(window, bg='black', fg='deep sky blue', width=30, text='GUI by @LinuxGuyOfficial ( GitHub )   \nIMGHide by @TechRaj156 ( YouTube )', font=('TkHeadingFont',9,'normal'))
author_label.place(relx = 1, rely = 1.0, anchor ='se')

window.mainloop()