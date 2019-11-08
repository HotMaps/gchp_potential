
CELERY_BROKER_URL_DOCKER = 'amqp://admin:mypass@rabbit:5672/'
CELERY_BROKER_URL_LOCAL = 'amqp://localhost/'


CM_REGISTER_Q = 'rpc_queue_CM_register' # Do no change this value

CM_NAME = 'CM - Shallow geothermal potential'
RPC_CM_ALIVE= 'rpc_queue_CM_ALIVE' # Do no change this value
RPC_Q = 'rpc_queue_CM_compute' # Do no change this value
CM_ID = 10 # CM_ID is defined by the enegy research center of Martigny (CREM)
PORT_LOCAL = int('500' + str(CM_ID))
PORT_DOCKER = 80

#TODO ********************setup this URL depending on which version you are running***************************

CELERY_BROKER_URL = CELERY_BROKER_URL_DOCKER
PORT = PORT_DOCKER

#TODO ********************setup this URL depending on which version you are running***************************

TRANFER_PROTOCOLE ='http://'
INPUTS_CALCULATION_MODULE = [
    {'input_name': 'Heating Season [0-365] expressed in days',
     'input_type': 'input',
     'input_parameter_name': 'heating_season_value',
     'input_value': 180,
     'input_priority': 0,
     'input_unit': 'd',
     'input_min': 30,
     'input_max': 365,
     'cm_id': CM_ID  # Do no change this value
     },
    {'input_name': 'Depth-Averaged Ground Thermal Capacity ρc',
     'input_type': 'input',
     'input_parameter_name': 'ground_capacity_value',
     'input_value': 2,
     'input_priority': 1,
     'input_unit': 'MJ m-3 K-1',
     'input_min': 1.,
     'input_max': 4.,
     'cm_id': CM_ID  # Do no change this value
     },
#    {'input_name': 'Value with the initial ground temperature T0 [°C]',
#     'input_type': 'input',
#     'input_parameter_name': 'ground_temp_value',
#     'input_value': 9.,
#     'input_priority': 1,
#     'input_unit': '°C',
#     'input_min': 0.,
#     'input_max': 25.,
#     'cm_id': CM_ID  # Do no change this value
#     },
    {'input_name': 'Borehole radius',
     'input_type': 'input',
     'input_parameter_name': 'borehole_radius',
     'input_value': 0.075,
     'input_priority': 1,
     'input_unit': 'm',
     'input_min': 0.05,
     'input_max': 0.10,
     'cm_id': CM_ID  # Do no change this value
     },
    {'input_name': 'Borehole thermal resistence',
     'input_type': 'input',
     'input_parameter_name': 'borehole_resistence',
     'input_value': None,
     'input_priority': 1,
     'input_unit': 'm KW-1',
     'input_min': 0.06,
     'input_max': 0.12,
     'cm_id': CM_ID  # Do no change this value
     },
    {'input_name': 'Borehole length',
     'input_type': 'input',
     'input_parameter_name': 'borehole_length',
     'input_value': 100,
     'input_priority': 1,
     'input_unit': 'm',
     'input_min': 0.,
     'input_max': 99999999.,
     'cm_id': CM_ID  # Do no change this value
     },
    {'input_name': 'Pipe radius',
     'input_type': 'input',
     'input_parameter_name': 'pipe_radius',
     'input_value': 0.016,
     'input_priority': 1,
     'input_unit': 'm',
     'input_min': 0.001,
     'input_max': 0.05,
     'cm_id': CM_ID  # Do no change this value
     },
    {'input_name': 'Number of pipes in the borehole',
     'input_type': 'input',
     'input_parameter_name': 'number_pipes',
     'input_value': 4,
     'input_priority': 1,
     'input_unit': '-',
     'input_min': 1,
     'input_max': 999999,
     'cm_id': CM_ID  # Do no change this value
     },
    {'input_name': 'Thermal conductivity of the borehole filling (geothermal grout)',
     'input_type': 'input',
     'input_parameter_name': 'grout_conductivity',
     'input_value': 4,
     'input_priority': 2,
     'input_unit': 'W m-1 °K-1',
     'input_min': 1,
     #TODO: check "input_max"
     'input_max': 999999,
     'cm_id': CM_ID  # Do no change this value
     },
    {'input_name': 'Minimum or maximum fluid temperature',
     'input_type': 'input',
     'input_parameter_name': 'fluid_limit_temperature',
     'input_value': -2,
     'input_priority': 1,
     'input_unit': '°C',
     #TODO: check "input_min" and "input_max"
     'input_min': -5,
     'input_max': 999999,
     'cm_id': CM_ID  # Do no change this value
     },
    {'input_name': 'Simulated lifetime of the plant',
     'input_type': 'input',
     'input_parameter_name': 'lifetime',
     'input_value': 50,
     'input_priority': 1,
     'input_unit': 'years',
     #TODO: check "input_min" and "input_max"
     'input_min': 1,
     'input_max': 999999,
     'cm_id': CM_ID  # Do no change this value
     }
]


SIGNATURE = {

    "category": "Supply",
    "authorized_scale":["NUTS 2","NUTS 0","Hectare"],
    "cm_name": CM_NAME,
    "layers_needed": [
        "land_surface_temperature",
    ],
    "type_layer_needed": [
        {"type": "land_surface_temperature"}
    ],
    "vectors_needed": [
        "shallow_geothermal_potential"
    ],
    "cm_url": "Do not add something",
    "cm_description": "This module aims to compute the Ground Source"
                      "Heat Pump (GSHP) potential of a selected area."
                      "It is based on the GRASS-GISS module "
                      "r.green.gshp.theoretical."
                      "The code is on Hotmaps Github group and has"
                      " been developed by EURAC",
    "cm_id": CM_ID,
    'inputs_calculation_module': INPUTS_CALCULATION_MODULE
}
