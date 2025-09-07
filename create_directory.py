from pathlib import Path
import gdsfactory as gf
import json

def create_wafer_dir(gds: gf.Component, dir_name: str, design_json: str) -> None:
    """
    Creates a nested directory structure for wafer design files and saves the GDS file and design JSON.
    Args:
        gds (gf.Component): The GDS component to be saved.
        dir_name (str): The name of the main directory to be created.
        design_json (str): The design JSON content to be saved in the Design directory.
    example for design_json:
    {
  "wafer name": "20250907_",
  "material": "Silicon",
  "size": 76200,
  "thickness": 1,
  "recipe": "NORMAL",
  "samples": [
    {
      "name": "Sample1",
      "dimension": [
        15000,
        5000
      ],
      "center": [
        0,
        0
      ],
      "jopherson junctions": [
        {
          "type": "DOLAN",
          "gap": 1,
          "name": "A"
        },
        {
          "type": "DOLAN",
          "gap": 1,
          "name": "B"
        }
      ],
      "resistance measurement points": [
        {
          "point": "(0,0)",
          "name": "A"
        },
        {
          "point": "(1,1)",
          "name": "B"
        }
      ]
    },
    {
      "name": "Sample2",
      "dimension": [
        15000,
        5000
      ],
      "center": [
        0,
        0
      ],
      "jopherson junctions": [
        {
          "type": "DOLAN",
          "gap": 1,
          "name": "A"
        },
        {
          "type": "DOLAN",
          "gap": 1,
          "name": "B"
        }
      ],
      "resistance measurement points": [
        {
          "point": "(0,0)",
          "name": "A"
        },
        {
          "point": "(1,1)",
          "name": "B"
        }
      ]
    }
  ],
  "test junctions": [
    {
      "type": "DOLAN",
      "BRIDGE START GAP": 1,
      "BRIDGE END GAP": 5,
      "LEFT FINGER": {
        "layer": "(1, 0)",
        "length": 10,
        "width": 1
      },
      "RIGHT FINGER": {
        "layer": "(1, 0)",
        "length": 10,
        "width": 1
      }
    }
  ]
}
    """


    # Specify the nested directory structure
    main_dir_path = Path("I:\\SergeR_Group\\Notes\\Fabrication\\" + dir_name)

    # Create nested directories
    main_dir_path.mkdir(parents=True, exist_ok=True)
    print(f"Nested directories '{main_dir_path}' created successfully.")

    design_dir_path = main_dir_path.joinpath("Design")
    design_dir_path.mkdir(parents=True, exist_ok=True)
    print(f"Nested directories '{design_dir_path}' created successfully.")

    gds.write_gds(design_dir_path.joinpath("testing.gds"), with_metadata=False)

    with design_dir_path.joinpath("data.json").open("w", encoding ="utf-8") as f:
        f.write(design_json)
    
    resistance_dir_path = main_dir_path.joinpath("Resistance")
    resistance_dir_path.mkdir(parents=True, exist_ok=True)
    print(f"Nested directories '{resistance_dir_path}' created successfully.")

    rCsv: str = "Sample,Point,Resistance (Ohm)\n"
    design_data: dict = json.loads(design_json)
    for sample in design_data["samples"]:
        sample_name: str = sample["name"]
        for rmp in sample["resistance measurement points"]:
            rCsv += f"{sample_name},{rmp['name']},\n"

    print(rCsv)

    with resistance_dir_path.joinpath("resistance.csv").open("w", encoding ="utf-8") as f:
        f.write(rCsv)

def create_design_json(wafer_name: str,
                       wafer_material: str,
                       wafer_size: float,
                       wafer_thickness: str,
                       recipe: str,
                       samples: list,
                       test_junctions: dict
                       ) -> str:
        # Json to have:
        # wafer name
        # material 
        # size
        # thickness
        # recipe
        # samples:
        #   name
        #   dimension
        #   center
        #   jopherson junctions:
        #       jj_N style
        #       jj_N width
        #       jj_N gap
        # test junctions:
        #   type:
        #       DOLAN
        #       DOLATHAN
        #       MANHANTAN
        #    BRIDGE START GAP
        #    BRIDGE END GAP
        #    FINGER WIDTH
    rtn: dict = {}
    rtn['wafer name'] = wafer_name
    rtn['material'] = wafer_material
    rtn['size'] = wafer_size
    rtn['thickness'] = wafer_thickness
    rtn['recipe'] = recipe
    rtn['samples'] = samples
    rtn['test junctions'] = test_junctions

    return json.dumps(rtn)