import extract_
import ortools_
import re
import streamlit as st


def main(lat_long, start_idx, end_idx, priority_locs, p_d, time_lim):

    output_G_maps_URL, final_points = ortools_.optimize(
        lat_long, start_idx, end_idx, priority_locs, p_d, time_lim)
    if len(final_points) <= 25:
        st.write(f"[Optimized Route 🚛]({output_G_maps_URL})")
    else:
        st.write(f"Optimized Route 🚛")
        st.write(
            f"Apparently GMaps URL doesn't work for more than 25 nodes 🙁. Check 'Show Co-Ordinates'.")
    if agree:
        st.json(final_points)


def check_seq(s, nmax):
    if s == "":
        return True
    pattern = re.compile(r"^\d+(,\d+)*$")
    match = pattern.match(s)
    if match:
        numbers = [int(n) for n in s.split(",")]
        return all(1 <= n <= nmax for n in numbers) and len(numbers) > 1
    else:
        return False


def check_seq_pd(s, nmax):
    if s == "":
        return True
    pattern = re.compile(r"^\d+(,\d+)*$")
    match = pattern.match(s)
    if match:
        numbers = [int(n) for n in s.split(",")]
        return all(1 <= n <= nmax for n in numbers) and len(numbers) % 2 == 0
    else:
        return False


if __name__ == "__main__":

    st.set_page_config(
        page_title="MultiStopOPT",
        page_icon="🛣️",
        layout="centered",
        initial_sidebar_state="auto"
    )

    st.subheader("Optimize Multi-Stop Routes on Google Maps 🗺️")

    num_loc = st.number_input(
        "Num_Locations across all URLs (Max 150)\n", min_value=2, max_value=150, step=1)
    num_urls = st.number_input("Num_URLs\n", min_value=1, max_value=15, step=1)
    urls = []
    for i in range(num_urls):
        url = st.text_input("G_Maps URL\n", key=i)
        urls.append(url)
    start_idx = st.number_input("Start_Location (Locations are numbered from 1 and follow the URL sequence. 0 implies not fixed.) \n",
                                min_value=0, max_value=num_loc, step=1, value=0)
    end_idx = st.number_input(
        "End_Location\n", min_value=0, max_value=num_loc, step=1, value=0)
    priority_locs = st.text_input(
        "Locations that will follow a fixed sequence in the final route (E.g. input 3,5,10 => locations 3, 5 and 10 will be in this order)\n")
    p_d = st.text_input(
        "Pickup & Delivery (E.g. input 3,5,5,12,15,17 => 3->5, 5->12 and 15->17) \n")
    time_lim = st.number_input(
        "Time_Limit (sec)\n", min_value=1, max_value=60, step=1, value=1)
    agree = st.checkbox("Show Co-Ordinates")
    if st.button("Optimize 🔧"):
        if "" not in urls and ((start_idx == 0 and end_idx == 0) or (start_idx != end_idx)):
            lat_long = extract_.get_lat_long(urls, num_loc)
            try:
                assert ((-1, -1) not in lat_long)
                assert (check_seq(priority_locs, num_loc))
                assert (check_seq_pd(p_d, num_loc))
                main(lat_long, start_idx, end_idx,
                     priority_locs, p_d, time_lim)
            except:
                if ((-1, -1) in lat_long):
                    st.write("Check Num_Locations 🙁.")
                elif (check_seq(priority_locs, num_loc) == 0):
                    st.write("Check Fixed Sequence 🙁.")
                elif (check_seq_pd(p_d, num_loc) == 0):
                    st.write("Check Pickup & Delivery 🙁.")
                else:
                    st.write(
                        "Error 🙁. One possible reason could be constraints contradicting each other ❌")
        else:
            if "" in urls:
                st.write("Check URLs 🙁.")
            elif (start_idx == end_idx):
                st.write("Start_Location can't be same as End_Location 🙁.")

    st.subheader("About 📃")
    st.write("Powered by Google OR-Tools [Apache License 2.0](https://github.com/google/or-tools/blob/92eab40155d5566039c92662632f196174f8da47/LICENSE) and geopy [MIT License](https://github.com/geopy/geopy/blob/ef48a8cbb85f842c0820333e53e7ebde7db382a3/LICENSE)")
    st.write(
        "Copyright (c) 2022 [Regista6](https://github.com/Regista6), [Repo](https://github.com/Regista6/MultiStopOPT)")
