import datetime # usada para colocar o timestamp em cada bloco
import json
import hashlib
import time
from flask import Flask, jsonify

class Blockchain:
    """
        Classe que constroi e armazena a blockchain

        Cada bloco da blockchain é um dicionário contendo 4 atributos:
        `index`: indice do bloco na lista blockchain 
        `timestamp`: marcador temporal de quando o bloco foi criado/minerado
        `proof`: valor referente ao proof of work usado na mineração do bloco
        `previous_hash`: hash do bloco anterior (para linkar um bloco cronologicamente a outro)
    """
    def __init__(self):
        """
            Método que inicializa a lista que conterá os blocos da blockchain,
            e insere nela o bloco genesis (primeiro bloco da estrutura)
        """
        self.chain = []

        # a hash é passad como 0 pois esse bloco não tem um bloco antecedente
        self.create_blockchain(proof=1, previous_hash='0')


    def create_blockchain(self, proof, previous_hash):
        """
            Método que cria um bloco que será inserido na blockchain

            - `param`: proof - valor referente ao proof of work usado na mineração do bloco
            - `param`: previous_hash - hash do bloco anterior ao bloco sendo criado

            - `return`: o bloco criado (dicionario)
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash
        }

        self.chain.append(block)
        return block

    def get_previous_block(self):
        """
            Método que retorna o ultimo bloco da blockchain

            - `return`: ultimo bloco da lista chain
        """
        last_block = self.chain[-1]
        return last_block

    def proof_of_work(self, previous_proof):
        """
            Método em que é realizada a busca pelo valor de proof que gere uma hash de acordo com uma 
            dificuldade (a hash deve ser iniciada com 4 zeros), até que esta seja encontrada,
            para que então o bloco seja mineirado 

            - `param`: previous_proof - valor proof do último bloco da cadeia

            - `return`: valor do novo proof
        """
        # novo proof pelo qual será feita a busca
        new_proof = 1
        # status da busca
        check_proof = False

        start_time = time.time()

        # a busca é feita até que se encontre uma hash de acordo com a dificuldade
        while check_proof is False:
            
            # o algoritmo a ser resolvido é baseado no novo valor do proof e no anterior, de forma a "linkar" os blocos 
            # e o valor hash é criptografado em hexadecimal
            # esse algoritmo é escolhido para que não ocorra um caso em que o new_proof e previous_proof estejam invertidos e resultem
            # em um mesmo proof, já o quadrado é para que a subtração não resulte sempre em 1
            hash_operation = hashlib.sha256(str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            
            # verifica se a hash esta de acordo com a dificuldade (iniciar com 4 zeros)
            # ps: quanto mais zeros maior a dificuldade da busca
            if hash_operation[:7] == '0000000':
                check_proof = True
            else:
                # modifica o valor do novo proof caso não for encontrado
                new_proof += 1

        end_time = time.time()
        print('tempo:', end_time - start_time)
        return new_proof

    def hash(self, block):
        """
            Método que criptografa o bloco e retorna o hash do bloco 

            - `param`: block - bloco pelo qual será gerada a hash
            - `return`: hash do bloco
        """
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    
    def is_chain_valid(self, chain):
        """
            Método que verifica a validade da blockchain, para preservar a integridade da mesma

            - `param`: chain - cadeia blockchain que será verificada
            - `return`: True caso a cadeia esteja integra e False caso não esteja
        """
        
        # pega o bloco genesis como bloco anterior
        previous_block = chain[0]
        block_index = 1

        # Itera pela cadeia a partir do segundo bloco (sendo o primeiro o genesis, utilizado como bloco anterior)
        while block_index < len(chain):
            # Bloco atual
            block = chain[block_index]

            # Verifica se o bloco atual está linkado ao bloco anterior (previous hash igual a hash do bloco anterior)
            # Se não tiver, então a cadeia não é valida
            if block["previous_hash"] != self.hash(previous_block):
                return False

            # Verifica se a hash dp valor de proof atual, quando passado pelo algoritmo (utilizando também o proof anterior)
            # passa pelo dificuldade atual definida (iniciar com 4 zeros)
            previous_proof = previous_block['proof']
            current_proof = block['proof']
            hash_operation = hashlib.sha256(str(current_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            
            # Verifica a operação hash, caso não estiver de acordo com a dificuldade, a cadeia não é valida
            if hash_operation[:7] != '0000000':
                return False

            # Modifica o bloco anterior e o atual e segue verificando a cadeia
            previous_block = block
            block_index += 1

        # Caso em que nenhum bloco está invalido, retorna True
        return True


###################################################################################
# Etapa flask - criar aplicação web para criar a blockchain e mineirar blocos 


app = Flask(__name__)

blockchain = Blockchain()


@app.route('/mine_block', methods=['GET'])
def mine_block():
   # get the data we need to create a block
   previous_block = blockchain.get_previous_block()
   previous_proof = previous_block['proof']
   proof = blockchain.proof_of_work(previous_proof)
   previous_hash = blockchain.hash(previous_block)

   block = blockchain.create_blockchain(proof, previous_hash)
   response = {'message': 'Block mined!',
               'index': block['index'],
               'timestamp': block['timestamp'],
               'proof': block['proof'],
               'previous_hash': block['previous_hash']}
   return jsonify(response), 200


@app.route('/get_chain', methods=['GET'])
def get_chain():
   response = {'chain': blockchain.chain,
               'length': len(blockchain.chain)}
   return jsonify(response), 200



app.run(host='0.0.0.0', port=5000)
