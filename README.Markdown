Postal Management System
------------------------

The Postal Management System is designed to ease the process of picking, packing, and posting items for small
Internet-based sellers. It integrates with retail sites (currently only Tindie) to download orders, generates
mailing and customs labels and prints them, and integrates with postage providers (currently only Royal Mail)
to generate and upload manifests / posting documents.

Configuration
=============

PMS reads its configuration from several configuration files.

Tindie configuration is stored in ~/.tindierc, and should look something like this:

    [auth]
    username=username
    password=password
    auth_token=some_token

Royal Mail configuration is stored in ~/.rmrc, and should look something like this:

    [account]
    number=12345
    service_register=01
    posting_location=12345
    email=example@example.com
    password=password

    [settings]
    auto_confirm=N

PMS specific configuration is stored in pms.conf in the root directory, and looks like this:

    [labels]
    return_address: An Address
        A street
        A country
    image=ppi_image.tif
    image_width=54
    image_height=14
    print_command=lpr

    [customs]
    image=cn22.png
    print_command=lpr -o PageSize=Custom.62x62mm


TODO
====

 - Automatically print out the Royal Mail manifest when uploading a posting
 - Generate Posting objects for each uploaded posting
 - Support marking a posting as shipped
 - Improve UI to filter out obsolete choices for products, postage methods, etc
 
