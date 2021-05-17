# Tracing autonomous systems
This application allows you to get information about the routers (ip address, autonomous system number, country and city) 
through which the packet passes to the specified node.

### Description
* Enter a domain name or IP address. 
* The script starts tracing to the specified node.
* The autonomous system and the location of each of the received IP addresses of the routers are determined. 

### Utilities

* To search for ip addresses of routers, use the "tracert" utility.
* To get the information of autonomous systems, use the site [ipinfo.io](https://ipinfo.io/)

### Using 

`python3 traceas.py [address | ip]`

`python3  traceas.py vk.com`

`python3  traceas.py 87.240.139.194`

### Author 
*Vasily Boyarskikh* ([vabyars](https://github.com/vabyars))