from pymol import cmd

def get_residue_range(self, obj_name):
    if not obj_name or obj_name == "Select a file.":
        return
    try:
        chains = cmd.get_chains(obj_name)
        self.curr_chain_residues = {}
        for c in chains:
            resi_list = []
            cmd.iterate(f"{obj_name} and chain {c} and name CA", "resi_list.append(resv)",
                        space={"resi_list": resi_list})

            if resi_list:
                self.curr_chain_residues[c] = [min(resi_list), max(resi_list)]
            else:
                self.box_res_id.setRange(0, 0)
                self.box_res_id.setValue(0)

        self.update_chain_combo_box()

    except Exception as e:
        print(f"Error getting residue range: {e}")
        self.box_res_id.setRange(0, 0)
        self.box_res_id.setValue(0)

def update_residue_range(self):
    try:
        selected_chain = self.chain_combo_box.currentText()
        min_resi, max_resi = self.curr_chain_residues[selected_chain]
        self.box_res_id.setRange(min_resi, max_resi)
        self.box_res_id.setValue(min_resi)
    except KeyError as e:
        print(f"Error updating residue range: {e}")