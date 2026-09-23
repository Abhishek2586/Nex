"""Generate a project-local CA and loopback server certificate."""
from datetime import datetime, timedelta, timezone
from ipaddress import ip_address
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

root=Path(__file__).resolve().parents[1]
target=root/'runtime/control/certs'; target.mkdir(parents=True,exist_ok=True)
ca_key_path=target/'ca.key'; ca_path=target/'ca.pem'; server_key_path=target/'server.key'; server_path=target/'server.pem'
if all(path.exists() for path in [ca_key_path,ca_path,server_key_path,server_path]):
    print(target); raise SystemExit(0)
now=datetime.now(timezone.utc)
ca_key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
ca_name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'NEXORA Project Local CA')])
ca_cert=(x509.CertificateBuilder().subject_name(ca_name).issuer_name(ca_name).public_key(ca_key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(now-timedelta(minutes=1)).not_valid_after(now+timedelta(days=30)).add_extension(x509.BasicConstraints(ca=True,path_length=0),critical=True).add_extension(x509.KeyUsage(digital_signature=True,key_encipherment=False,key_cert_sign=True,key_agreement=False,content_commitment=False,data_encipherment=False,crl_sign=True,encipher_only=False,decipher_only=False),critical=True).sign(ca_key,hashes.SHA256()))
server_key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
server_name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'localhost')])
server_cert=(x509.CertificateBuilder().subject_name(server_name).issuer_name(ca_name).public_key(server_key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(now-timedelta(minutes=1)).not_valid_after(now+timedelta(days=7)).add_extension(x509.SubjectAlternativeName([x509.DNSName('localhost'),x509.IPAddress(ip_address('127.0.0.1'))]),critical=False).add_extension(x509.BasicConstraints(ca=False,path_length=None),critical=True).add_extension(x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]),critical=False).sign(ca_key,hashes.SHA256()))
ca_key_path.write_bytes(ca_key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
ca_path.write_bytes(ca_cert.public_bytes(serialization.Encoding.PEM))
server_key_path.write_bytes(server_key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
server_path.write_bytes(server_cert.public_bytes(serialization.Encoding.PEM))
print(target)
