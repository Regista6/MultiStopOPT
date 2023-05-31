import re
import streamlit as st


'''
https://www.google.com/maps/dir/Knockdown+Center/Roberta's,+261+Moore+St,+Brooklyn,+NY+11206,+United+States/40.6983609,-73.9088167/@40.7062513,-73.9058627,14z
/data=!4m15!4m14!1m5!1m1!1s0x89c25ea2cb53d0a9:0xe6dd93729a094800!2m2!1d-73.914068!2d40.7153921!1m5!1m1!1s0x89c25d0d3ab223cd:0x16b11fd586b90f7d!2m2!1d-73.9335781!2d40.7050612!1m0!3e0

Above is a typical Google Maps Route URL having 3 locations.
'''

# TODO: Make everything cleaner.


def f1(link, lat_long):
    '''Extract (lat, long) before the 'data' field from GMaps route URL.'''
    parts = link.split('@')
    decimals = re.findall(r'-?\d+\.\d+', parts[0])
    for i in range(0, len(decimals)-1, 2):
        lat, long = float(decimals[i]), float(decimals[i+1])
        lat_long.append((lat, long))


def extract(l, a):  # recursive algorithm for extracting items from a list of lists and items
    if type(a) is list:
        for item in a:
            extract(l, item)
    else:
        l.append(a)


def f2(link, lat_long, num_loc):  # https://gist.github.com/jeteon/e71fa21c1feb48fe4b5eeec045229a0c
    '''Extract (lat, long) by decoding the 'data' field of GMaps route URL.'''
    index = link.find('=')
    str1 = link[index+1:]
    parts = str1.split('!')
    parts = [x for x in parts if x]  # Remove empty elements
    root = []  # Root elemet
    curr = root  # Current array element being appended to
    m_stack = [root,]  # Stack of "m" elements
    m_count = [len(parts),]  # Number of elements to put under each level
    for el in parts:
        kind = el[1]
        value = el[2:]
        # Decrement all the m_counts
        for i in range(len(m_count)):
            m_count[i] -= 1
        if kind == 'm':  # Add a new array to capture coming values
            new_arr = []
            m_count.append(int(value))
            curr.append(new_arr)
            m_stack.append(new_arr)
            curr = new_arr
        else:
            if kind == 'b':  # Assuming these are boolean
                curr.append(value == '1')
            elif kind in ['d', 'f']:  # Float or double
                curr.append(float(value))
            elif kind in ['i', 'u', 'e']:  # Integer, unsigned or enum as int
                curr.append(int(value))
            else:  # Store anything else as a string
                curr.append(value)

    # Pop off all the arrays that have their values already
    root_list = []
    try:
        while m_count[-1] == 0:
            m_stack.pop()
            m_count.pop()
            curr = m_stack[-1]
    except IndexError:
        # Handle the error here
        pass
    l = []
    extract(l, root)
    l = [elem for elem in l if type(elem) == float]

    j = 0
    cnt1 = 0
    for i in range(num_loc):
        if j >= (len(l)-1):
            break
        if lat_long[i] == (-1, -1):
            lat_long[i] = ((l[j+1], l[j]))
            j += 2
            cnt1 += 1

    return cnt1


def f3(url):
    '''Extract everything between 'dir' and '@' from GMaps Route URL.'''
    match = re.search(r"dir(.+?)@", url)
    text = ""
    if match:
        text = match.group(1)
    else:
        st.write("Regex Fail ")
    substrings = re.split(r"(?<!\\)/(?!\\)", text)
    substrings = [x for x in substrings if x]
    return substrings


def f4(url):
    '''Extract coordinates of the center from GMaps Route URL'''
    result = re.search(r"@(.+?)data", url)
    if result:
        matched_string = result.group(1)
        center = "@" + matched_string.rstrip("/")
        return center

def f5(url):
    '''Remove '?entry=ttu' from the end of the url.'''
    url = re.sub(r'\?entry=ttu$', '', url)
    return url

def get_lat_long(urls, num_loc):
    '''Extract (latitude, longitude) from Google Maps Route URL with original order maintained.'''
    lat_long = [(-1, -1)] * (num_loc)
    lat_long1 = []
    # This is to ensure final output url loc_names are same as that of the original
    loc_identifier = []
    cnt = 0
    for url in urls:
        url = f5(url)
        elem = f3(url)
        lat_long1.clear()
        f1(url, lat_long1)
        for (lat_, long_) in lat_long1:
            str1 = str(lat_) + ","+str(long_)
            idx = elem.index(str1)
            if (idx+cnt) < num_loc:
                lat_long[idx+cnt] = (lat_, long_)
        loc_identifier += elem
        cnt += len(lat_long1)
        cnt += f2(url, lat_long, num_loc)
    center = f4(urls[0])
    loc_identifier.append(center)
    return lat_long, loc_identifier
