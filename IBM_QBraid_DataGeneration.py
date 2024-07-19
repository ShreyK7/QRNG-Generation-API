from qbraid.runtime.qiskit import QiskitRuntimeProvider

from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.circuit.library import QuantumVolume
from qiskit.visualization.counts_visualization import plot_histogram
from qiskit import QuantumCircuit

from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.providers.jobstatus import JobStatus

import numpy as np

import os
from dotenv import load_dotenv

allowed_devices = ['ibm_brisbane', 'ibm_kyoto', 'ibm_sherbrooke', 'ibm_osaka']

def generate_data(length, numLines, machine=None):
    load_dotenv()
    API_KEY = os.getenv('IBM_APIKEY')
    provider = QiskitRuntimeProvider(API_KEY)
    
    HGate_circ = QuantumCircuit(100)
    for i in range(0, 100):
        HGate_circ.h(i)
    HGate_circ.measure_all()

    if not machine:
        machine = get_least_busy_device()
    
    device = provider.get_device(machine)
    output = 'using device ' + machine + ' (QPU obtained)'
    print(output)

    pm = generate_preset_pass_manager(optimization_level=1, target=device._backend.target)
    transpiled_circuit = pm.run(HGate_circ)
    shot_count = (length*numLines)/100
    job = device.run(transpiled_circuit, shots=shot_count, memory=True)
    print('job running')

    result = job.result()
    rawData = result.measurements()
    print('job completed')

    unbrokenData = []
    for shot in rawData:
        for meas in shot:
            unbrokenData.append(meas)

    results = []
    for i in range(0, len(unbrokenData), length):
        results.append(''.join(map(str, unbrokenData[i:i+length])))

    print({'data': results})

    return results

def launch_job(length=100, numLines=1, machine=None):
    API_KEY = os.getenv('IBM_APIKEY')
    provider = QiskitRuntimeProvider(API_KEY)
    
    HGate_circ = QuantumCircuit(100)
    for i in range(0, 100):
        HGate_circ.h(i)
    HGate_circ.measure_all()

    if not machine:
        machine = get_least_busy_device()
    
    device = provider.get_device(machine)
    output = 'using device ' + machine + ' (QPU obtained)'
    print(output)

    pm = generate_preset_pass_manager(optimization_level=1, target=device._backend.target)
    transpiled_circuit = pm.run(HGate_circ)
    shot_count = (length*numLines)/100
    job = device.run(transpiled_circuit, shots=shot_count, memory=True)
    output =  f'job running on device {machine}, jobID = {job._job_id}'
    print('job running')
    return output

def get_job_status(jobID):
    API_KEY = os.getenv('IBM_APIKEY')
    provider = QiskitRuntimeService('ibm_quantum', API_KEY)
    job = provider.job(jobID)
    if job.status() == JobStatus.QUEUED:
        queueInfo = job.queue_info()
        output = f'job {jobID} is queued: estimated start time is {queueInfo.estimated_start_time}, queue position is {queueInfo.position}. Call the /QRNG/JobStatus/<jobID> endpoint later to check for job completion'
    elif job.status() == JobStatus.DONE:
        output = f'job {jobID} has run succesfully on device {job._backend.name}. Call the /QRNG/JobResults/<jobID> endpoint to get QRNG data in JSON'
    else:
        output = job.status()

    return [output]
    
def get_least_busy_device():
    API_KEY = os.getenv('IBM_APIKEY')
    provider = QiskitRuntimeProvider(API_KEY)
    return provider.least_busy().id

def get_job_results(jobID):
    API_KEY = os.getenv('IBM_APIKEY')
    provider = QiskitRuntimeService('ibm_quantum', API_KEY)
    job = provider.job(jobID)

#print(launch_job())
#print(get_job_status('ctd1a0gy6ybg008tn780'))