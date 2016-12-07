PRISMed - Server
=======================

Server unit of the PRISMed platform. 


**To install just type:**
```
python setup.py install
```

**Dependencies**

All python packages are automatically installed by *pip*. Anyway, it is mandatory to previously install mongodb. E.g. In ubuntu type:
```
sudo apt-get install mongodb
```


## About the RSA key generation

The RSA key is generated through part of the code shown below:


from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Key generation and storage (Just once at the server side)
key = RSA.generate(2048)
f = open('prismed_key.pem','w')
f.write(key.exportKey())
f.close()


# Encryption at the client
f = open('prismed_key.pem')
pubkey = RSA.importKey(f.read()).publickey()#send this key to the client
# (At the client) then the client uses it to encrypt
cipher = PKCS1_OAEP.new(pubkey)
ciphertext = cipher.encrypt("15340959-5")


# The encrypted message is received at the server side and decrypted
privkey = RSA.importKey(open('prismed_key.pem').read())
cipher = PKCS1_OAEP.new(privkey)
cipher.decrypt(ciphertext)
