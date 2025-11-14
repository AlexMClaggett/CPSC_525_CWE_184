


my_dict = dict()
my_dict["Jeff"] = ("old", "grey")
my_dict["Mammoth"] = ("cute", "brown")
my_dict["Owl"] = ("WHHOOOO", "white")



key = next((k for k, v in my_dict.items() if "grey" in v), None)
if key != None:
    print(f"I found {key}")
