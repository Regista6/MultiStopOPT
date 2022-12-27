import re
import streamlit as st

'''
https://www.google.com/maps/dir/Knockdown+Center/Roberta's,+261+Moore+St,+Brooklyn,+NY+11206,+United+States/40.6983609,-73.9088167/@40.7062513,-73.9058627,14z
/data=!4m15!4m14!1m5!1m1!1s0x89c25ea2cb53d0a9:0xe6dd93729a094800!2m2!1d-73.914068!2d40.7153921!1m5!1m1!1s0x89c25d0d3ab223cd:0x16b11fd586b90f7d!2m2!1d-73.9335781!2d40.7050612!1m0!3e0

Above is a typical GMaps URL having 3 locations. 
f1() extracts coordinates of locations before "data". These locations have no names associated with them.
f1() will extract (40.6983609, -73.9088167) from the above URL.
f2() on the other hand decodes the "data" string and extracts coordinates of locations present there. f2() can sometimes get
coordinates already extracted by f1().
Using f1(), f2() and f3(), coordinates of all locations are extracted in the original order.

'''

# TODO: Make everything cleaner.


def f1(link, lat_long):
    parts = link.split('@')
    decimals = re.findall(r'-?\d+\.\d+', parts[0])
    for i in range(0, len(decimals)-1, 2):
        lat, long = float(decimals[i]), float(decimals[i+1])
        lat_long.append((round(lat, 10), round(long, 10)))


def extract(l, a):  # recursive algorithm for extracting items from a list of lists and items
    if type(a) is list:
        for item in a:
            extract(l, item)
    else:
        l.append(a)


def f2(link, lat_long, num_loc):  # https://gist.github.com/jeteon/e71fa21c1feb48fe4b5eeec045229a0c
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
            lat_long[i] = ((round(l[j+1], 10), round(l[j], 10)))
            j += 2
            cnt1 += 1

    return cnt1


def f3(url):
    match = re.search(r"dir(.+?)@", url)
    text = ""
    if match:
        text = match.group(1)
    else:
        st.write("Regex Fail ")
    substrings = re.split(r"(?<!\\)/(?!\\)", text)
    substrings = [x for x in substrings if x]
    return substrings


def get_lat_long(urls, num_loc):
    lat_long = [(-1, -1)] * (num_loc)
    lat_long1 = []
    cnt = 0
    for url in urls:
        elem = f3(url)
        lat_long1.clear()
        f1(url, lat_long1)
        for (lat_, long_) in lat_long1:
            str1 = str(lat_) + ","+str(long_)
            idx = elem.index(str1)
            if (idx+cnt) < num_loc:
                lat_long[idx+cnt] = (lat_, long_)
        cnt += len(lat_long1)
        cnt += f2(url, lat_long, num_loc)

    return lat_long
