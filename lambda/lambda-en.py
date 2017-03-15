# -*- coding: utf-8 -*-

import logging
import httplib
import re
import sys
import time
#from validation import validateResponse, validateContext

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SAMPLE_MANUFACTURER = 'Sample Manufacturer'
SAMPLE_APPLIANCES = [
    {
        'applianceId': 'Switch-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Switch',
        'version': '1',
        'friendlyName': 'Switch',
        'friendlyDescription': 'On/off switch that is functional and reachable',
        'isReachable': True,
        'actions': [
            'turnOn',
            'turnOff',
        ],
        'additionalApplianceDetails': {}        
    },
    {
        'applianceId': 'Dimmer-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Dimmer',
        'version': '1',
        'friendlyName': 'Upstairs Dimmer',
        'friendlyDescription': 'Dimmer that is functional and reachable',
        'isReachable': True,
        'actions': [
            'turnOn',
            'turnOff',
            'setPercentage',
            'incrementPercentage',
            'decrementPercentage',
        ],
        'additionalApplianceDetails': {}        
    },
    {
        'applianceId': 'Fan-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Fan',
        'version': '1',
        'friendlyName': 'Upstairs Fan',
        'friendlyDescription': 'Fan that is functional and reachable',
        'isReachable': True,
        'actions': [
            'turnOn',
            'turnOff',
            'setPercentage',
            'incrementPercentage',
            'decrementPercentage',
        ],
        'additionalApplianceDetails': {}        
    },
    {
        'applianceId': 'SwitchUnreachable-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Switch',
        'version': '1',
        'friendlyName': 'Switch Unreachable',
        'friendlyDescription': 'Switch that is unreachable and shows (Offline)',
        'isReachable': False,
        'actions': [
            'turnOn',
            'turnOff',
        ],
        'additionalApplianceDetails': {}
    },
    {
        'applianceId': 'ThermostatAuto-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Thermostat',
        'version': '1',
        'friendlyName': 'Family Room',
        'friendlyDescription': 'Thermostat in AUTO mode and reachable',
        'isReachable': True,
        'actions': [
            'setTargetTemperature',
            'incrementTargetTemperature',
            'decrementTargetTemperature',
            'getTargetTemperature',
            'getTemperatureReading',            
        ],
        'additionalApplianceDetails': {}
    },
    {
        'applianceId': 'ThermostatHeat-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Thermostat',
        'version': '1',
        'friendlyName': 'Guestroom',
        'friendlyDescription': 'Thermostat in HEAT mode and reachable',
        'isReachable': True,
        'actions': [
            'setTargetTemperature',
            'incrementTargetTemperature',
            'decrementTargetTemperature',
            'getTargetTemperature',
            'getTemperatureReading',            
        ],
        'additionalApplianceDetails': {}
    },
    {
        'applianceId': 'ThermostatCool-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Thermostat',
        'version': '1',
        'friendlyName': 'Hallway',
        'friendlyDescription': 'Thermostat in COOL mode and reachable',
        'isReachable': True,
        'actions': [
            'setTargetTemperature',
            'incrementTargetTemperature',
            'decrementTargetTemperature',
            'getTargetTemperature',
            'getTemperatureReading',            
        ],
        'additionalApplianceDetails': {}
    },
    {
        'applianceId': 'ThermostatEco-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Thermostat',
        'version': '1',
        'friendlyName': 'Kitchen',
        'friendlyDescription': 'Thermostat in ECO mode and reachable',
        'isReachable': True,
        'actions': [
            'setTargetTemperature',
            'incrementTargetTemperature',
            'decrementTargetTemperature',
            'getTargetTemperature',
            'getTemperatureReading',            
        ],
        'additionalApplianceDetails': {}
    },
    {
        'applianceId': 'ThermostatCustom-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Thermostat',
        'version': '1',
        'friendlyName': 'Laundry Room',
        'friendlyDescription': 'Thermostat in CUSTOM mode and reachable',
        'isReachable': True,
        'actions': [
            'setTargetTemperature',
            'incrementTargetTemperature',
            'decrementTargetTemperature',
            'getTargetTemperature',
            'getTemperatureReading',            
        ],
        'additionalApplianceDetails': {}
    },
    {
        'applianceId': 'ThermostatOff-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Thermostat',
        'version': '1',
        'friendlyName': 'Living Room',
        'friendlyDescription': 'Thermostat in OFF mode and reachable',
        'isReachable': True,
        'actions': [
            'setTargetTemperature',
            'incrementTargetTemperature',
            'decrementTargetTemperature',
            'getTargetTemperature',
            'getTemperatureReading',            
        ],
        'additionalApplianceDetails': {}
    },
    {
        'applianceId': 'Lock-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Lock',
        'version': '1',
        'friendlyName': 'Door',
        'friendlyDescription': 'Lock that is functional and reachable',
        'isReachable': True,
        'actions': [
            'setLockState',
            'getLockState',
        ],
        'additionalApplianceDetails': {}
    },
]

def lambda_handler(event,context):
    try:
        validateContext(context)

        logger.info('Request Header:{}'.format(event['header']))
        logger.info('Request Payload:{}'.format(event['payload']))

        response = {}
        if event['header']['namespace'] == 'Alexa.ConnectedHome.Discovery':
            response = handleDiscovery(event,context)      
        elif event['header']['namespace'] in ['Alexa.ConnectedHome.Control','Alexa.ConnectedHome.Query']:
            response = handleControl(event,context)

        logger.info('Response Header:{}'.format(response['header']))
        logger.info('Response Payload:{}'.format(response['payload']))

        validateResponse(event,response)     
        
        return response
    except ValueError as error:
        logger.error(error)
        raise
        
def handleDiscovery(event,context):
    response_name = 'DiscoverAppliancesResponse'
    header = generateResponseHeader(event,response_name)
    payload = {
       'discoveredAppliances': SAMPLE_APPLIANCES + generateSampleErrorAppliances()
    }
    response = generateResponse(header,payload)
    return response

def handleControl(event,context):
    payload = {}
    appliance_id = event['payload']['appliance']['applianceId']
    message_id = event['header']['messageId']
    request_name = event['header']['name']

    response_name = ''

    previous_temperature = 21.0
    minimum_temperature = 5.0
    maximum_temperature = 30.0

    if appliance_id == 'ThermostatAuto-001':
        previous_mode = 'AUTO'
        target_mode = 'AUTO'
        response = generateTemperatureResponse(event,previous_temperature,previous_mode,target_mode,minimum_temperature,maximum_temperature)

    elif appliance_id == 'ThermostatHeat-001':
        previous_mode = 'HEAT'
        target_mode = 'HEAT'
        response = generateTemperatureResponse(event,previous_temperature,previous_mode,target_mode,minimum_temperature,maximum_temperature)
    
    elif appliance_id == 'ThermostatCool-001':
        previous_mode = 'COOL'
        target_mode = 'COOL'
        response = generateTemperatureResponse(event,previous_temperature,previous_mode,target_mode,minimum_temperature,maximum_temperature)

    elif appliance_id == 'ThermostatEco-001':
        previous_mode = 'ECO'
        target_mode = 'ECO'
        response = generateTemperatureResponse(event,previous_temperature,previous_mode,target_mode,minimum_temperature,maximum_temperature)

    elif appliance_id == 'ThermostatCustom-001':
        previous_mode = 'CUSTOM'
        target_mode = 'CUSTOM'
        response = generateTemperatureResponse(event,previous_temperature,previous_mode,target_mode,minimum_temperature,maximum_temperature)

    elif appliance_id == 'ThermostatOff-001':
        previous_mode = 'OFF'
        target_mode = 'OFF'
        response = generateTemperatureResponse(event,previous_temperature,previous_mode,target_mode,minimum_temperature,maximum_temperature)

    elif appliance_id == 'Lock-001':
        if request_name == 'SetLockStateRequest':
            response_name = 'SetLockStateConfirmation'
            payload = {
                'lockState': event['payload']['lockState']
            }

        elif request_name == 'GetLockStateRequest':
            response_name = 'GetLockStateResponse'
            payload = {
                'lockState': 'UNLOCKED',
                'applianceResponseTimestamp': getUTCTimestamp()
            }
        header = generateResponseHeader(event,response_name)
        response = generateResponse(header,payload)

    elif isSampleErrorAppliance(appliance_id):
        response_name = appliance_id.replace('-001','')
        header = generateResponseHeader(event,response_name)
        payload = {}
        if response_name == 'ValueOutOfRangeError':
            payload = {
                'minimumValue': 5.0,
                'maximumValue': 30.0,
            }
        elif response_name == 'DependentServiceUnavailableError':
            payload = {
                'dependentServiceName': 'Customer Credentials Database',
            }
        elif response_name == 'TargetFirmwareOutdatedError' or response_name == 'TargetBridgeFirmwareOutdatedError':
            payload = {
                'minimumFirmwareVersion': '17',
                'currentFirmwareVersion': '6',
            }
        elif response_name.startswith('UnableToGetValueError') or response_name.startswith('UnableToSetValueError'):
            if response_name.startswith('UnableToGetValueError'):
                code = response_name.replace('UnableToGetValueError-','')
                header['namespace'] = 'Alexa.ConnectedHome.Query'
                header['name'] = 'UnableToGetValueError'
            else:
                code = response_name.replace('UnableToSetValueError-','')
                header['name'] = 'UnableToSetValueError'
            payload = {
                'errorInfo': {
                    'code': code,
                    'description': 'The requested operation cannot be completed because the device is ' + code,
                }
            }
            
        elif response_name == 'UnwillingToSetValueError':
            payload = {
                'errorInfo': {
                    'code': 'ThermostatIsOff',
                    'description': 'The requested operation is unsafe because it requires changing the mode.',
                }
            }
        elif response_name == 'RateLimitExceededError':
            payload = {
                'rateLimit': '10',
                'timeUnit': 'HOUR',
            }
        elif response_name == 'NotSupportedInCurrentModeError':
            payload = {
                'currentDeviceMode': 'AWAY',
            }
        elif response_name == 'UnexpectedInformationReceivedError':
            payload = {
                'faultingParameter': 'value',
            }

        response = generateResponse(header,payload)

    else:

        if request_name == 'TurnOnRequest': response_name = 'TurnOnConfirmation'
        if request_name == 'TurnOffRequest': response_name = 'TurnOffConfirmation'
        if request_name == 'SetTargetTemperatureRequest': 
            response_name = 'SetTargetTemperatureConfirmation'
            target_temperature = event['payload']['targetTemperature']['value']
            payload = {
                'targetTemperature': {
                    'value': target_temperature
                },
                'temperatureMode': {
                    'value': 'AUTO'
                },
                'previousState' : {
                    'targetTemperature':{
                        'value': 21.0
                    },
                    'temperatureMode':{
                        'value': 'AUTO'
                    }
                }
            }
        if request_name == 'IncrementTargetTemperatureRequest':
            response_name = 'IncrementTargetTemperatureConfirmation'
            delta_temperature = event['payload']['deltaTemperature']['value']
            payload = {
                'previousState': {
                    'temperatureMode': {
                        'value': 'AUTO'
                    },
                    'targetTemperature': {
                        'value': 21.0
                    }
                },
                'targetTemperature': {
                    'value': 21.0 + delta_temperature
                },
                'temperatureMode': {
                    'value': 'AUTO'
                }
            }        
        if request_name == 'DecrementTargetTemperatureRequest':
            response_name = 'DecrementTargetTemperatureConfirmation'
            delta_temperature = event['payload']['deltaTemperature']['value']
            payload = {
                'previousState': {
                    'temperatureMode': {
                        'value': 'AUTO'
                    },
                    'targetTemperature': {
                        'value': 21.0
                    }
                },
                'targetTemperature': {
                    'value': 21.0 - delta_temperature
                },
                'temperatureMode': {
                    'value': 'AUTO'
                }
            }        
        if request_name == 'SetPercentageRequest': response_name = 'SetPercentageConfirmation'
        if request_name == 'IncrementPercentageRequest': response_name = 'IncrementPercentageConfirmation'
        if request_name == 'DecrementPercentageRequest': response_name = 'DecrementPercentageConfirmation'
        
        if appliance_id == 'SwitchUnreachable-001':
            response_name = 'TargetOfflineError'
    
        header = generateResponseHeader(event,response_name)
        response = generateResponse(header,payload)

    return response

# utility functions
def generateSampleErrorAppliances():
    # this should be in sync with same list in validation.py
    VALID_CONTROL_ERROR_RESPONSE_NAMES = [
        'ValueOutOfRangeError',
        'TargetOfflineError',
        'BridgeOfflineError',
        'NoSuchTargetError',
        'DriverInternalError',
        'DependentServiceUnavailableError',
        'TargetConnectivityUnstableError',
        'TargetBridgeConnectivityUnstableError',
        'TargetFirmwareOutdatedError',
        'TargetBridgeFirmwareOutdatedError',
        'TargetHardwareMalfunctionError',
        'TargetBridgeHardwareMalfunctionError',
        'UnableToGetValueError',
        'UnableToSetValueError',
        'UnwillingToSetValueError',
        'RateLimitExceededError',
        'NotSupportedInCurrentModeError',
        'ExpiredAccessTokenError',
        'InvalidAccessTokenError',
        'UnsupportedTargetError',
        'UnsupportedOperationError',
        'UnsupportedTargetSettingError',
        'UnexpectedInformationReceivedError'
    ]
    sample_error_appliances = []
    
    device_number = 1

    for error in VALID_CONTROL_ERROR_RESPONSE_NAMES:
        if error in ['UnableToGetValueError','UnableToSetValueError']:
            VALID_UNABLE_ERROR_INFO_CODES = [
                'DEVICE_AJAR',
                'DEVICE_BUSY',
                'DEVICE_JAMMED',
                'DEVICE_OVERHEATED',
                'HARDWARE_FAILURE',
                'LOW_BATTERY',
                'NOT_CALIBRATED'
            ]
            for code in VALID_UNABLE_ERROR_INFO_CODES:
                friendly_name = generateErrorFriendlyName(device_number) + ' door'
                if error == 'UnableToGetValueError':
                    friendly_description = 'Utterance: Alexa, is ' + friendly_name + ' locked? Response: ' + error + ' code: ' + code    
                else:
                    friendly_description = 'Utterance: Alexa, lock ' + friendly_name + '. Response: ' + error + ' code: ' + code    

                sample_error_appliance = {
                    'applianceId': error + '-' + code + '-001',
                    'manufacturerName': SAMPLE_MANUFACTURER,
                    'modelName': 'Lock',
                    'version': '1',
                    'friendlyName': friendly_name,
                    'friendlyDescription': friendly_description,
                    'isReachable': True,
                    'actions': [
                        'setLockState',
                        'getLockState',                        
                    ],
                    'additionalApplianceDetails': {}
                }

                sample_error_appliances.append(sample_error_appliance)
                device_number = device_number + 1

        else:
            friendly_name = generateErrorFriendlyName(device_number)
            friendly_description = 'Utterance: Alexa, turn on ' + friendly_name + '. Response: ' + error    

            sample_error_appliance = {
                'applianceId': error + '-001',
                'manufacturerName': SAMPLE_MANUFACTURER,
                'modelName': 'Switch',
                'version': '1',
                'friendlyName': friendly_name,
                'friendlyDescription': friendly_description,
                'isReachable': True,
                'actions': [
                    'turnOn',
                    'turnOff',                        
                ],
                'additionalApplianceDetails': {}
            }

            if error == 'ValueOutOfRangeError':
                sample_error_appliance['friendlyDescription'] = 'Utterance: Alexa, set ' + friendly_name + ' to 80 degrees. Response: ' + error
                sample_error_appliance['modelName'] = 'Thermostat'
                sample_error_appliance['actions'] = [
                    'setTargetTemperature',
                    'incrementTargetTemperature',
                    'decrementTargetTemperature',
                ]

            sample_error_appliances.append(sample_error_appliance)
            device_number = device_number + 1

    return sample_error_appliances

def isSampleErrorAppliance(appliance_id):
    sample_error_appliances = generateSampleErrorAppliances()
    for sample_error_appliance in sample_error_appliances:
        if sample_error_appliance['applianceId'] == appliance_id: return True
    return False

def generateResponseHeader(request,response_name):
    header = {
        'namespace': request['header']['namespace'],
        'name': response_name,
        'payloadVersion': '2',
        'messageId': request['header']['messageId'],        
    }
    return header

def generateResponse(header,payload):
    response = {
        'header': header,
        'payload': payload,
    }
    return response

def generateTemperatureResponse(request,previous_temperature,previous_mode,target_mode,minimum_temperature,maximum_temperature):
    request_name = request['header']['name']
    message_id = request['header']['messageId']
    
    # valid request    
    if request_name in ['SetTargetTemperatureRequest','IncrementTargetTemperatureRequest','DecrementTargetTemperatureRequest']:
        if request_name == 'SetTargetTemperatureRequest': 
            response_name = 'SetTargetTemperatureConfirmation'
            target_temperature = request['payload']['targetTemperature']['value']
        if request_name == 'IncrementTargetTemperatureRequest':
            response_name = 'IncrementTargetTemperatureConfirmation'
            target_temperature = previous_temperature + request['payload']['deltaTemperature']['value']
        if request_name == 'DecrementTargetTemperatureRequest':
            response_name = 'DecrementTargetTemperatureConfirmation'
            target_temperature = previous_temperature - request['payload']['deltaTemperature']['value']

        payload = {
            'targetTemperature': {
                'value': target_temperature
            },
            'temperatureMode': {
                'value': target_mode
            },
            'previousState' : {
                'targetTemperature':{
                    'value': previous_temperature
                },
                'temperatureMode':{
                    'value': previous_mode
                }
            }        
        }
    elif request_name == 'GetTemperatureReadingRequest':
        response_name = 'GetTemperatureReadingResponse'
        payload = {
            'temperatureReading': {
                'value': 21.00,
            }
        }

    elif request_name == 'GetTargetTemperatureRequest':
        response_name = 'GetTargetTemperatureResponse'
        payload = {
            'applianceResponseTimestamp': getUTCTimestamp(),
            'temperatureMode': {
                'value': target_mode,
                'friendlyName': '',
            }
        }

        if target_mode in ['HEAT','COOL','ECO','CUSTOM']:
            payload['targetTemperature'] = {
                'value': 21.00,
            }
        elif target_mode in ['AUTO']:
            payload['coolingTargetTemperature'] = {
                'value': 23.00
            }
            payload['heatingTargetTemperature'] = {
                'value': 19.00
            }

        if target_mode == 'CUSTOM':
            payload['temperatureMode']['friendlyName'] = 'Manufacturer custom mode'


    else:
        response_name = 'UnexpectedInformationReceivedError'
        payload = {
            'faultingParameter': 'request.name: ' + request_name
        }

    header = generateResponseHeader(request,response_name)
    response = generateResponse(header,payload)
    return response

def generateErrorFriendlyName(device_number):
    return 'Device ' + str(device_number)


"""Utility functions."""

def getUTCTimestamp(seconds=None):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(seconds))





# validation.py

# -*- coding: utf-8 -*-

# Copyright 2016-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the "License"). You may not use this file except in 
# compliance with the License. A copy of the License is located at
# 
#     http://aws.amazon.com/asl/
# 
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific 
# language governing permissions and limitations under the License.

"""Alexa Smart Home API Validation Package for Python.

This module is used by Alexa Smart Home API third party (3P) developers to validate their Lambda 
responses before sending them back to Alexa. If an error is found, an exception is thrown so that 
the 3P can catch the error and do something about it, instead of sending it back to Alexa and 
causing an error on the Alexa side.

The validations are based on the current public Alexa Smart Home API reference:
https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference
"""

import logging
import re
import sys

"""Various constants used in validation."""

VALID_DISCOVERY_REQUEST_NAMES = [
    'DiscoverAppliancesRequest'
]
VALID_CONTROL_REQUEST_NAMES = [
    'TurnOnRequest',
    'TurnOffRequest',
    'SetTargetTemperatureRequest',
    'IncrementTargetTemperatureRequest',
    'DecrementTargetTemperatureRequest',
    'SetPercentageRequest',
    'IncrementPercentageRequest',
    'DecrementPercentageRequest',
    'SetLockStateRequest'
]
VALID_QUERY_REQUEST_NAMES = [
    'GetLockStateRequest',
    'GetTemperatureReadingRequest',
    'GetTargetTemperatureRequest'
]
VALID_SYSTEM_REQUEST_NAMES = [
    'HealthCheckRequest'
]
VALID_REQUEST_NAMES = VALID_DISCOVERY_REQUEST_NAMES + VALID_QUERY_REQUEST_NAMES + VALID_CONTROL_REQUEST_NAMES + VALID_SYSTEM_REQUEST_NAMES

VALID_DISCOVERY_RESPONSE_NAMES = [
    'DiscoverAppliancesResponse'
]
VALID_CONTROL_RESPONSE_NAMES = [
    'TurnOnConfirmation',
    'TurnOffConfirmation',
    'SetTargetTemperatureConfirmation',
    'IncrementTargetTemperatureConfirmation',
    'DecrementTargetTemperatureConfirmation',
    'SetPercentageConfirmation',
    'IncrementPercentageConfirmation',
    'DecrementPercentageConfirmation',
    'SetLockStateConfirmation'
]
VALID_CONTROL_ERROR_RESPONSE_NAMES = [
    'ValueOutOfRangeError',
    'TargetOfflineError',
    'BridgeOfflineError',
    'NoSuchTargetError',
    'DriverInternalError',
    'DependentServiceUnavailableError',
    'TargetConnectivityUnstableError',
    'TargetBridgeConnectivityUnstableError',
    'TargetFirmwareOutdatedError',
    'TargetBridgeFirmwareOutdatedError',
    'TargetHardwareMalfunctionError',
    'TargetBridgeHardwareMalfunctionError',
    'UnableToGetValueError',
    'UnableToSetValueError',
    'UnwillingToSetValueError',
    'RateLimitExceededError',
    'NotSupportedInCurrentModeError',
    'ExpiredAccessTokenError',
    'InvalidAccessTokenError',
    'UnsupportedTargetError',
    'UnsupportedOperationError',
    'UnsupportedTargetSettingError',
    'UnexpectedInformationReceivedError'
]
VALID_QUERY_RESPONSE_NAMES = [
    'GetLockStateResponse',
    'GetTemperatureReadingResponse',
    'GetTargetTemperatureResponse'
]
VALID_SYSTEM_RESPONSE_NAMES = [
    'HealthCheckResponse'
]
VALID_RESPONSE_NAMES = VALID_DISCOVERY_RESPONSE_NAMES + VALID_CONTROL_RESPONSE_NAMES + VALID_CONTROL_ERROR_RESPONSE_NAMES + VALID_QUERY_RESPONSE_NAMES + VALID_SYSTEM_RESPONSE_NAMES

VALID_NON_EMPTY_PAYLOAD_RESPONSE_NAMES = [
    'SetTargetTemperatureConfirmation',
    'IncrementTargetTemperatureConfirmation',
    'DecrementTargetTemperatureConfirmation',
    'GetTemperatureReadingResponse',
    'GetTargetTemperatureResponse',
    'SetLockStateConfirmation',
    'GetLockStateResponse',
    'ValueOutOfRangeError',
    'DependentServiceUnavailableError',
    'TargetFirmwareOutdatedError',
    'TargetBridgeFirmwareOutdatedError',
    'UnableToGetValueError',
    'UnableToSetValueError',
    'UnwillingToSetValueError',
    'RateLimitExceededError',
    'NotSupportedInCurrentModeError',
    'UnexpectedInformationReceivedError'
]
VALID_ACTIONS = [
    'decrementPercentage',
    'decrementTargetTemperature',
    'getTargetTemperature',
    'getTemperatureReading',
    'getLockState',
    'incrementPercentage',
    'incrementTargetTemperature',
    'setLockState',
    'setPercentage',
    'setTargetTemperature',
    'turnOff',
    'turnOn'
]
VALID_TEMPERATURE_MODES = [
    'HEAT',
    'COOL',
    'AUTO',
    'ECO',
    'OFF',
    'CUSTOM'
]
VALID_CURRENT_DEVICE_MODES = [
    'HEAT',
    'COOL',
    'AUTO',
    'AWAY',
    'OTHER'
]
VALID_UNABLE_ERROR_INFO_CODES = [
    'DEVICE_AJAR',
    'DEVICE_BUSY',
    'DEVICE_JAMMED',
    'DEVICE_OVERHEATED',
    'HARDWARE_FAILURE',
    'LOW_BATTERY',
    'NOT_CALIBRATED'
]
VALID_UNWILLING_ERROR_INFO_CODES = [
    'ThermostatIsOff'
]
VALID_TIME_UNITS = [
    'MINUTE',
    'HOUR',
    'DAY'
]
VALID_LOCK_STATES = [
    'LOCKED',
    'UNLOCKED'
]
REQUIRED_HEADER_KEYS = [
    'namespace',
    'name',
    'payloadVersion',
    'messageId'
]
REQUIRED_RESPONSE_KEYS = [
    'header',
    'payload'
]
REQUIRED_DISCOVERED_APPLIANCE_KEYS = [
    'applianceId',
    'manufacturerName',
    'modelName',
    'version',
    'friendlyName',
    'friendlyDescription',
    'isReachable',
    'actions',
    'additionalApplianceDetails'
]
MAX_DISCOVERED_APPLIANCES = 300


def validateContext(context):
    """Validate the Lambda context.

    Currently, this method just checks to ensure that the Lambda timeout is set to 7 seconds or less.
    This is to ensure that your Lambda times out and errors before Alexa times out (8 seconds), 
    allowing you to see the timeout error. Otherwise, you could take > 8 seconds to respond and even
    though you think you have responded properly and without error, Alexa actually timed out resulting
    in an error to the user.
    """

    if context.get_remaining_time_in_millis() > 7000: raise_value_error(generate_error_message('Lambda','timeout must be 7 seconds or less',context))


def validateResponse(request,response):
    """Validate the response to a request.

    This is the main validation method to be called in your Lambda handler, just before you return
    the response to Alexa. This method validates the request to ensure it is valid, and then dispatches
    to specific response validation methods depending on the request namespace.
    """

    # Validate request
    if request is None: raise_value_error(generate_error_message('Request','request is missing',request))
    if not bool(request): raise_value_error(generate_error_message('Request','request must not be empty',request))
    if not isinstance(request,dict): raise_value_error(generate_error_message('Request','request must be a dict',request))
    try:
        request_namespace = request['header']['namespace']
    except:
        raise_value_error(generate_error_message('Request','request is invalid',request))

    # Validate response
    if response is None: raise_value_error(generate_error_message('Response','response is missing',response))
    if not bool(response): raise_value_error(generate_error_message('Response','response must not be empty',response))
    if not isinstance(response,dict): raise_value_error(generate_error_message('Response','response must be a dict',response))

    for required_key in REQUIRED_RESPONSE_KEYS:
        if required_key not in response: raise_value_error(generate_error_message('Response',format(required_key) + ' is missing',response))

    if request_namespace == 'Alexa.ConnectedHome.Discovery':
        validateDiscoveryResponse(request,response)
    elif request_namespace == 'Alexa.ConnectedHome.Control':
        validateControlResponse(request,response)
    elif request_namespace == 'Alexa.ConnectedHome.Query':
        validateQueryResponse(request,response)
    elif request_namespace == 'Alexa.ConnectedHome.System':
        validateSystemResponse(request,response)
    else:
        raise_value_error(generate_error_message('Request','request.header.namespace is invalid',request))

def validateSystemResponse(request,response):
    """Validate the response to a Health Check request.

    This method validates the response to a Health Check request, based on the API reference:
    https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#health-check-messages
    """ 

    # Validate header
    validateResponseHeader(request,response)
    response_name = response['header']['name']

    # Validate response payload
    try:
        payload = response['payload']
    except:
        raise_value_error(generate_error_message(response_name,'payload is missing',response))

    if payload is None: raise_value_error(generate_error_message(response_name,'payload is missing',payload))

    for required_key in ['description','isHealthy']:
        if required_key not in payload: raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' is missing',payload))
        if is_empty_string(payload['description']): raise_value_error(generate_error_message(response_name,'payload.description must not be empty',payload))
        if not isinstance(payload['isHealthy'],bool): raise_value_error(generate_error_message(response_name,'payload.isHealthy must be a boolean',payload))

def validateDiscoveryResponse(request,response):
    """Validate the response to a DiscoverApplianceRequest request.

    This method validates the response to a DiscoverApplianceRequest request, based on the API reference:
    https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#discoverappliancesresponse
    """ 

    # Validate header
    validateResponseHeader(request,response)
    response_name = response['header']['name']

    # Validate response payload
    try:
        payload = response['payload']
    except:
        raise_value_error(generate_error_message(response_name,'payload is missing',response))

    if payload is None: raise_value_error(generate_error_message(response_name,'payload is missing',payload))
    if not isinstance(payload,dict): raise_value_error(generate_error_message(response_name,'payload must be a dict',payload))

    if 'discoveredAppliances' not in payload: raise_value_error(generate_error_message(response_name,'payload.discoveredAppliances is missing',payload))
    if not isinstance(payload['discoveredAppliances'],list): raise_value_error(generate_error_message(response_name,'payload.discoveredAppliances must be a list',payload))
    if len(payload['discoveredAppliances']) > MAX_DISCOVERED_APPLIANCES: raise_value_error(generate_error_message(response_name,'payload.discoveredAppliances must not contain more than 300 appliances',payload))

    # Validate each discovered appliance
    for discoveredAppliance in payload['discoveredAppliances']:
        
        for required_key in REQUIRED_DISCOVERED_APPLIANCE_KEYS:
            if required_key not in discoveredAppliance: raise_value_error(generate_error_message(response_name,format(required_key) + ' is missing',discoveredAppliance))

        if is_empty_string(discoveredAppliance['applianceId']): raise_value_error(generate_error_message(response_name,'applianceId must not be empty',discoveredAppliance))
        if len(discoveredAppliance['applianceId']) > 256: raise_value_error(generate_error_message(response_name,'applianceId must not exceed 256 characters',discoveredAppliance))
        if not re.match('^[a-zA-Z0-9_\-=#;:?@&]*$',discoveredAppliance['applianceId']): raise_value_error(generate_error_message(response_name,'applianceId must be alphanumeric or include these special characters: _-=#;:?@&',discoveredAppliance))
        if is_empty_string(discoveredAppliance['manufacturerName']): raise_value_error(generate_error_message(response_name,'manufacturerName must not be empty',discoveredAppliance))
        if len(discoveredAppliance['manufacturerName']) > 128: raise_value_error(generate_error_message(response_name,'manufacturerName must not exceed 128 characters',discoveredAppliance))
        if is_empty_string(discoveredAppliance['modelName']): raise_value_error(generate_error_message(response_name,'modelName must not be empty',discoveredAppliance))
        if len(discoveredAppliance['modelName']) > 128: raise_value_error(generate_error_message(response_name,'modelName must not exceed 128 characters',discoveredAppliance))
        if is_empty_string(discoveredAppliance['version']): raise_value_error(generate_error_message(response_name,'version must not be empty',discoveredAppliance))
        if len(discoveredAppliance['version']) > 128: raise_value_error(generate_error_message(response_name,'version must not exceed 128 characters',discoveredAppliance))
        if is_empty_string(discoveredAppliance['friendlyName']): raise_value_error(generate_error_message(response_name,'friendlyName must not be empty',discoveredAppliance))
        if len(discoveredAppliance['friendlyName']) > 128: raise_value_error(generate_error_message(response_name,'friendlyName must not exceed 128 characters',discoveredAppliance))
        if not is_alphanumeric_and_spaces(discoveredAppliance['friendlyName']): raise_value_error(generate_error_message(response_name,'friendlyName must be specified in alphanumeric characters and spaces',discoveredAppliance))
        if is_empty_string(discoveredAppliance['friendlyDescription']): raise_value_error(generate_error_message(response_name,'friendlyDescription must not be empty',discoveredAppliance))
        if len(discoveredAppliance['friendlyDescription']) > 128: raise_value_error(generate_error_message(response_name,'friendlyDescription must not exceed 128 characters',discoveredAppliance))
        if not isinstance(discoveredAppliance['isReachable'],bool): raise_value_error(generate_error_message(response_name,'isReachable must be a boolean',discoveredAppliance))
        if not isinstance(discoveredAppliance['actions'],list): raise_value_error(generate_error_message(response_name,'actions must be a list',discoveredAppliance))
        if len(discoveredAppliance['actions']) == 0: raise_value_error(generate_error_message(response_name,'actions must not be empty',discoveredAppliance))

        for action in discoveredAppliance['actions']:
            if action not in VALID_ACTIONS: raise_value_error(generate_error_message(response_name,format(action) + ' is an invalid action',discoveredAppliance))

        if discoveredAppliance['additionalApplianceDetails'] is not None:
            if sys.getsizeof(discoveredAppliance['additionalApplianceDetails']) > 5000: raise_value_error(generate_error_message(response_name,'additionalApplianceDetails must not exceed 5000 bytes',discoveredAppliance))


def validateControlResponse(request,response):
    """Validate the response to a Control request.

    This method validates the response to a Control (e.g. turn on/off, set temperatures, etc.) request, based on the API reference (starting from):
    https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#onoff-messages
    """ 

    # Validate header
    validateResponseHeader(request,response)
    request_name = request['header']['name']
    response_name = response['header']['name']

    # Validate response payload
    try:
        payload = response['payload']
    except:
        raise_value_error(generate_error_message(response_name,'payload is missing',response))

    if payload is None: raise_value_error(generate_error_message(response_name,'payload is missing',payload))
    if not isinstance(payload,dict): raise_value_error(generate_error_message(response_name,'payload must be a dict',payload))

    # Validate non-empty control response payload
    if response_name not in VALID_NON_EMPTY_PAYLOAD_RESPONSE_NAMES:
        if bool(payload): raise_value_error(generate_error_message(response_name,'payload must be empty',payload))
    else:
        if not bool(payload): raise_value_error(generate_error_message(response_name,'payload must not be empty',payload))

    # Validate thermostat control response payload
    if response_name in ['SetTargetTemperatureConfirmation','IncrementTargetTemperatureConfirmation','DecrementTargetTemperatureConfirmation']: 
        # Validate payload
        for required_key in ['targetTemperature','temperatureMode','previousState']:
            if required_key not in payload: raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' is missing',payload))
        if 'value' not in payload['targetTemperature']: raise_value_error(generate_error_message(response_name,'payload.targetTemperature.value is missing',payload))
        if not is_number(payload['targetTemperature']['value']): raise_value_error(generate_error_message(response_name,'payload.targetTemperature.value must be a number',payload))
        if 'value' not in payload['temperatureMode']: raise_value_error(generate_error_message(response_name,'payload.temperatureMode.value is missing',payload))
        if payload['temperatureMode']['value'] not in VALID_TEMPERATURE_MODES: raise_value_error(generate_error_message(response_name,'payload.temperatureMode.value is invalid',payload))

        # Validate payload.previousState
        for required_key in ['targetTemperature','temperatureMode']:
            if required_key not in payload['previousState']: raise_value_error(generate_error_message(response_name,'payload.previousState.' + format(required_key) + ' is missing',payload))
        if 'value' not in payload['previousState']['targetTemperature']: raise_value_error(generate_error_message(response_name,'payload.previousState.targetTemperature.value is missing',payload))
        if not is_number(payload['previousState']['targetTemperature']['value']): raise_value_error(generate_error_message(response_name,'payload.previousState.targetTemperature.value must be a number',payload))
        if 'value' not in payload['previousState']['temperatureMode']: raise_value_error(generate_error_message(response_name,'payload.previousState.temperatureMode.value is missing',payload))
        if payload['previousState']['temperatureMode']['value'] not in VALID_TEMPERATURE_MODES: raise_value_error(generate_error_message(response_name,'payload.previousState.temperatureMode.value is invalid',payload))

    # Validate lock control response payload
    if response_name in ['SetLockStateRequest']:
        for required_key in ['lockState']:
            if required_key not in payload: raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' is missing',payload))
        if payload['lockState'] not in VALID_LOCK_STATES: raise_value_error(generate_error_message(response_name,'payload.lockState is invalid',payload))

    # Validate control error response payload
    if response_name == 'ValueOutOfRangeError':
        for required_key in ['minimumValue','maximumValue']:
            if required_key not in payload: raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' is missing',payload))
            if not is_number(payload[required_key]): raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' must be a number',payload))

    if response_name == 'DependentServiceUnavailableError':
        required_key = 'dependentServiceName'
        if required_key not in payload: raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' is missing',payload))
        if not is_alphanumeric_and_spaces(payload[required_key]): raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' must be specified in alphanumeric characters and spaces',payload))

    if response_name in ['TargetFirmwareOutdatedError','TargetBridgeFirmwareOutdatedError']:
        for required_key in ['minimumFirmwareVersion','currentFirmwareVersion']:
            if required_key not in payload: raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' is missing',payload))
            if is_empty_string(payload[required_key]): raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' must not be empty',payload))
            if not is_alphanumeric(payload[required_key]): raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' must be specified in alphanumeric characters',payload))

    if response_name == 'UnableToSetValueError':
        required_key = 'errorInfo'
        if required_key not in payload: raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' is missing',payload))
        for required_key in ['code','description']:
            if required_key not in payload['errorInfo']: raise_value_error(generate_error_message(response_name,'payload.errorInfo' + format(required_key) + ' is missing',payload))
        if payload['errorInfo']['code'] not in VALID_UNABLE_ERROR_INFO_CODES: raise_value_error(generate_error_message(response_name,'payload.errorInfo.code is invalid',payload))

    if response_name == 'UnableToGetValueError': validateQueryResponse(request,response) # this is a really ugly hack

    if response_name == 'UnwillingToSetValueError':
        required_key = 'errorInfo'
        if required_key not in payload: raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' is missing',payload))
        for required_key in ['code','description']:
            if required_key not in payload['errorInfo']: raise_value_error(generate_error_message(response_name,'payload.errorInfo' + format(required_key) + ' is missing',payload))
        if payload['errorInfo']['code'] not in VALID_UNWILLING_ERROR_INFO_CODES: raise_value_error(generate_error_message(response_name,'payload.errorInfo.code is invalid',payload))

    if response_name == 'RateLimitExceededError':
        for required_key in ['rateLimit','timeUnit']:
            if required_key not in payload: raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' is missing',payload))
        if not payload['rateLimit'].isdigit(): raise_value_error(generate_error_message(response_name,'payload.rateLimit must be a positive integer',payload))
        if payload['timeUnit'] not in VALID_TIME_UNITS: raise_value_error(generate_error_message(response_name,'payload.timeUnit is invalid',payload))

    if response_name == 'NotSupportedInCurrentModeError':
        required_key = 'currentDeviceMode'
        if required_key not in payload: raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' is missing',payload))
        if payload[required_key] not in VALID_CURRENT_DEVICE_MODES: raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' is invalid',payload))

    if response_name == 'UnexpectedInformationReceivedError':
        required_key = 'faultingParameter'
        if required_key not in payload: raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' is missing',payload))
        if is_empty_string(payload[required_key]): raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' must not be empty',payload))

def validateQueryResponse(request,response):
    """Validate the response to a Query request.

    This method validates the response to a Query (e.g. ambient temperature, lock state, etc.) request, based on the API reference (starting from):
    https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#onoff-messages
    """ 

    # Validate header
    validateResponseHeader(request,response)
    response_name = response['header']['name']

    # Validate response payload
    try:
        payload = response['payload']
    except:
        raise_value_error(generate_error_message(response_name,'payload is missing',response))

    if payload is None: raise_value_error(generate_error_message(response_name,'payload is missing',payload))
    if not isinstance(payload,dict): raise_value_error(generate_error_message(response_name,'payload must be a dict',payload))

    # Validate non-empty control response payload
    if response_name not in VALID_NON_EMPTY_PAYLOAD_RESPONSE_NAMES:
        if bool(payload): raise_value_error(generate_error_message(response_name,'payload must be empty',payload))
    else:
        if not bool(payload): raise_value_error(generate_error_message(response_name,'payload must not be empty',payload))

    # Validate thermostat query response payload
    if response_name in 'GetTemperatureReadingResponse': 
        for required_key in ['temperatureReading']:
            if required_key not in payload: raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' is missing',payload))
        if 'value' not in payload['temperatureReading']: raise_value_error(generate_error_message(response_name,'payload.temperatureReading.value is missing',payload))
        if not is_number(payload['temperatureReading']['value']): raise_value_error(generate_error_message(response_name,'payload.temperatureReading.value must be a number',payload))

    if response_name in 'GetTargetTemperatureResponse': 
        for required_key in ['temperatureMode']:
            if required_key not in payload: raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' is missing',payload))
        if 'value' not in payload['temperatureMode']: raise_value_error(generate_error_message(response_name,'payload.temperatureMode.value is missing',payload))
        if payload['temperatureMode']['value'] not in VALID_TEMPERATURE_MODES: raise_value_error(generate_error_message(response_name,'payload.temperatureMode.value is invalid',payload))

        mode = payload['temperatureMode']['value']

        for optional_key in ['targetTemperature','coolingTargetTemperature','heatingTargetTemperature']:
            if optional_key in payload:
                if 'value' not in payload[optional_key]: raise_value_error(generate_error_message(response_name,'payload.' + optional_key + '.value is missing',payload))
                if not is_number(payload[optional_key]['value']): raise_value_error(generate_error_message(response_name,'payload.' + optional_key + '.value must be a number',payload))

        if mode == 'CUSTOM':
            if 'friendlyName' not in payload['temperatureMode']: raise_value_error(generate_error_message(response_name,'payload.temperatureMode.friendlyName is missing',payload))
            if is_empty_string(payload['temperatureMode']['friendlyName']): raise_value_error(generate_error_message(response_name,'payload.temperatureMode.friendlyName must not be empty',payload))

    # Validate lock query response payload
    if response_name in ['GetLockStateRequest']:
        for required_key in ['lockState']:
            if required_key not in payload: raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' is missing',payload))
        if payload['lockState'] not in VALID_LOCK_STATES: raise_value_error(generate_error_message(response_name,'payload.lockState is invalid',payload))

    # Validate query error response payload
    if response_name == 'UnableToGetValueError':
        required_key = 'errorInfo'
        if required_key not in payload: raise_value_error(generate_error_message(response_name,'payload.' + format(required_key) + ' is missing',payload))
        for required_key in ['code','description']:
            if required_key not in payload['errorInfo']: raise_value_error(generate_error_message(response_name,'payload.errorInfo' + format(required_key) + ' is missing',payload))
        if payload['errorInfo']['code'] not in VALID_UNABLE_ERROR_INFO_CODES: raise_value_error(generate_error_message(response_name,'payload.errorInfo.code is invalid',payload))


def validateResponseHeader(request,response):
    """Validate the response header.

    This method validates the header of the responses, based on the API reference:
    https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#skill-adapter-directives
    """ 

    request_name = request['header']['name']
    header = response['header']

    # Validate if request_name is valid
    if request_name not in VALID_REQUEST_NAMES: raise_value_error(generate_error_message('Request','request name is invalid',request))

    # Validate if header exists
    if header is None: raise_value_error(generate_error_message('Response','response header is missing',response))

    # Validate header required params
    for required_header_key in REQUIRED_HEADER_KEYS:
        if required_header_key not in header: raise_value_error(generate_error_message('Response','header.' + required_header_key + ' is required',header))

    # Validate header namespace and name
    if request_name in VALID_DISCOVERY_REQUEST_NAMES:
        if header['namespace'] != 'Alexa.ConnectedHome.Discovery': raise_value_error(generate_error_message('Discovery Response','header.namespace must be Alexa.ConnectedHome.Discovery',header))
        if header['name'] not in VALID_DISCOVERY_RESPONSE_NAMES: raise_value_error(generate_error_message('Discovery Response','header.name is invalid',header))
        correct_response_name = request_name.replace('Request','Response')
        if header['name'] != correct_response_name: raise_value_error(generate_error_message('Discovery Response','header.name must be ' + correct_response_name + ' for ' + request_name,header))

    if request_name in VALID_CONTROL_REQUEST_NAMES:
        if header['namespace'] not in ['Alexa.ConnectedHome.Query','Alexa.ConnectedHome.Control']: raise_value_error(generate_error_message('Control Response','header.namespace must be Alexa.ConnectedHome.Query or Alexa.ConnectedHome.Control',header))
        if header['name'] not in VALID_CONTROL_RESPONSE_NAMES + VALID_CONTROL_ERROR_RESPONSE_NAMES: raise_value_error(generate_error_message('Control Response','header.name is invalid',header))
        if header['name'] not in VALID_CONTROL_ERROR_RESPONSE_NAMES:
            correct_response_name = request_name.replace('Request','Confirmation')
            if header['name'] != correct_response_name: raise_value_error(generate_error_message('Control Response','header.name must be an error response name or ' + correct_response_name + ' for ' + request_name,header))

    if request_name in VALID_QUERY_REQUEST_NAMES:
        if header['namespace'] not in ['Alexa.ConnectedHome.Query','Alexa.ConnectedHome.Control']: raise_value_error(generate_error_message('Query Response','header.namespace must be Alexa.ConnectedHome.Query or Alexa.ConnectedHome.Control',header))
        if header['name'] not in VALID_QUERY_RESPONSE_NAMES + VALID_CONTROL_ERROR_RESPONSE_NAMES: raise_value_error(generate_error_message('Query Response','header.name is invalid',header))
        if header['name'] not in VALID_CONTROL_ERROR_RESPONSE_NAMES:
            correct_response_name = request_name.replace('Request','Response')
            if header['name'] != correct_response_name: raise_value_error(generate_error_message('Query Response','header.name must be an error response name or ' + correct_response_name + ' for ' + request_name,header))
    
    if request_name in VALID_SYSTEM_REQUEST_NAMES:
        if header['namespace'] != 'Alexa.ConnectedHome.System': raise_value_error(generate_error_message('System Response','header.namespace must be Alexa.ConnectedHome.System',header))
        if header['name'] not in VALID_SYSTEM_RESPONSE_NAMES: raise_value_error(generate_error_message('System Response','header.name is invalid',header))
        correct_response_name = request_name.replace('Request','Response')
        if header['name'] != correct_response_name: raise_value_error(generate_error_message('System Response','header.name must be ' + correct_response_name + ' for ' + request_name,header))
    
    # Validate common header constraints
    if header['payloadVersion'] != '2': raise_value_error(generate_error_message(header['name'],'header.payloadVersion must be \'2\' (string)',header))
    if not re.match('^[a-zA-Z0-9\-]*$',header['messageId']): raise_value_error(generate_error_message(header['name'],'header.messageId must be specified in alphanumeric characters or - ',header))
    if is_empty_string(header['messageId']): raise_value_error(generate_error_message(header['name'],'header.messageId must not be empty',header))
    if len(header['messageId']) > 127: raise_value_error(generate_error_message(header['name'],'header.messageId must not exceed 127 characters',header))


"""Utility functions."""

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_alphanumeric_and_spaces(s):
    return re.match('^[a-zA-Z0-9äüöÄÜÖß ]*$',s)

def is_alphanumeric(s):
    return re.match('^[a-zA-Z0-9äüöÄÜÖß]*$',s)    

def is_empty_string(s):
    return len(str(s).strip()) == 0

def raise_value_error(message):
    raise ValueError(message)

def generate_error_message(title,message,data):
    return title + ' :: ' + message + ': ' + format(data)
