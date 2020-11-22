import itertools
import time
import json
import glob
import architecture.LifeBoard


def does_generic(nb_generic, nb_envelope):
    return all([c1 == c2 or c1 == "-1" for c1, c2 in zip(nb_generic.split(","), nb_envelope.split(","))])


def special_nb_format(list_assignments, width, height):
    dicts = {",".join([str(b) for b in assignment_interior]): {} for assignment_interior in list_assignments}
    dir = "..\\preprocess\\new_boards_old_format\\"
    # new_boards_files = glob.glob(dir + "*.json")
    for assignment in list_assignments:
        f_name = dir + "cast_{}_{}_{}.json".format("".join([str(b) for b in assignment]), width, height)
        dict_cast = json.load(open(f_name, "r"))
        new_dict_cast = {}
        nbs_envelops = sorted(list(dict_cast.keys()), key=lambda nb_env: -nb_env.count("-1"))
        for nb_envelope in nbs_envelops:
            generic_nb_envelope = [nb_generic for nb_generic in new_dict_cast.keys()
                                   if does_generic(nb_generic, nb_envelope)]
            dict_obs = dict_cast[nb_envelope]
            if not generic_nb_envelope:
                new_dict_cast[nb_envelope] = dict_obs
            else:
                for nb_generic in generic_nb_envelope:
                    new_dict_cast[nb_generic].update(dict_obs)

        json.dump(new_dict_cast, open(f_name.replace("new_boards_old_format\\", ""), "w"))
        print("end ", len(dict_cast), len(new_dict_cast), assignment)
    return


def change_nb_format(list_assignments, width, height):
    # old format - nb_interior(file_name), nb_envelope - obs
    # new format - nb_interior(file_name), nb_envelope - {obs_envelope_str:obs}
    # specefic which has generic give their entries and deleted
    dicts = {",".join([str(b) for b in assignment_interior]): {} for assignment_interior in list_assignments}
    dir = "..\\preprocess\\new_boards_old_format\\"
    # new_boards_files = glob.glob(dir + "*.json")
    for assignment in list_assignments:
        f_name = dir + "cast_{}_{}_{}.json".format("".join([str(b) for b in assignment]), width, height)
        dict_cast = json.load(open(f_name, "r"))
        new_dict_cast = {}
        nbs_envelops = sorted(list(dict_cast.keys()), key=lambda nb_env: -nb_env.count("-1"))
        for nb_envelope in nbs_envelops:
            generic_nb_envelope = [nb_generic for nb_generic in new_dict_cast.keys()
                                   if does_generic(nb_generic, nb_envelope)]
            dict_obs = {architecture.LifeBoard.LifeBoard(string=ob, width=width, height=height)
                            .envelope_str(): ob for ob in dict_cast[nb_envelope]}
            if not generic_nb_envelope:
                new_dict_cast[nb_envelope] = dict_obs
            else:
                for nb_generic in generic_nb_envelope:
                    new_dict_cast[nb_generic].update(dict_obs)

        json.dump(new_dict_cast, open(f_name.replace("new_boards_old_format\\", ""), "w"))
        print("end ", len(dict_cast), len(new_dict_cast), assignment)
    return


def build_nb_format(list_assignments, width, height):
    dicts = {",".join([str(b) for b in assignment_interior]): {} for assignment_interior in list_assignments}
    dir = "..\\preprocess\\old_boards\\"
    old_boards_files = glob.glob(dir + "*.json")
    for f_name in old_boards_files:
        dict_cast = json.load(open(f_name, "r"))
        for interior in dicts.keys():
            if interior in dict_cast.keys():
                for envelope, ob in dict_cast[interior].items():
                    if envelope not in dicts[interior]:
                        dicts[interior][envelope] = {}
                    dicts[interior][envelope].update(
                        {architecture.LifeBoard.LifeBoard(string=ob, width=width, height=height)
                             .envelope_str(): ob for ob in dict_cast[interior][envelope]})

    # save dicts as files remove unnecasary keys
    for interior in dicts.keys():
        json.dump({envelope: list(dict_obs.values()) for envelope, dict_obs in dicts[interior].items()}
                  , open("..\\preprocess\\new_boards_old_format\\cast_{}_{}_{}.json".format(interior.replace(",", ""), width, height), "w"))
    return


if __name__ == "__main__":
    interior_bits = 9
    iter_assignments_interior = itertools.product([0, 1], repeat=interior_bits)
    list_assignments = list(iter_assignments_interior)[16:]
    tic = time.time()
    change_nb_format(list_assignments, 5, 5)
    print("time elpassed: {}".format(time.time() - tic))
