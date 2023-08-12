# Kuantum dolanıklığı için gerekli modülleri yükleme
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, Aer, execute

# Kuantum devresi oluşturma
q = QuantumRegister(2, 'q')
c = ClassicalRegister(2, 'c')
qc = QuantumCircuit(q, c)

# İlk kuantum parçacığını X kapısı ile hazırlama
qc.x(q[0])

# İlk kuantum parçacığını Hadamard kapısı ile geçirme
qc.h(q[0])

# Kuantum dolanıklığı oluşturma
qc.cx(q[0], q[1])

# İlk kuantum parçacığını ölçme
qc.measure(q[0], c[0])

# İkinci kuantum parçacığını ölçme
qc.measure(q[1], c[1])

# Simülasyon yapma
backend = Aer.get_backend('qasm_simulator')
job_sim = execute(qc, backend, shots=1024)
sim_result = job_sim.result()

# Sonuçları yazdırma
print(sim_result.get_counts(qc))
