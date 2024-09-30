from cryptography import x509
from cryptography.hazmat.primitives.serialization import pkcs12
import datetime

def get_pseudonym(cert):
    return cert.subject.get_attributes_for_oid(x509.NameOID.PSEUDONYM)[0].value

def cert_load(fname):
    """lê certificado de ficheiro"""
    with open(fname, "rb") as fcert:
        cert = x509.load_pem_x509_certificate(fcert.read())
    return cert


def cert_validtime(cert, now=None):
    """valida que 'now' se encontra no período
    de validade do certificado."""
    if now is None:
        now = datetime.datetime.now(tz=datetime.timezone.utc)
    if now < cert.not_valid_before_utc or now > cert.not_valid_after_utc:
        raise x509.verification.VerificationError(
            "Certificate is not valid at this time"
        )


def cert_validsubject(cert, attrs=[]):
    """verifica atributos do campo 'subject'. 'attrs'
    é uma lista de pares '(attr,value)' que condiciona
    os valores de 'attr' a 'value'."""
    print(cert.subject)
    for attr in attrs:
        if cert.subject.get_attributes_for_oid(attr[0])[0].value != attr[1]:
            raise x509.verification.VerificationError(
                "Certificate subject does not match expected value"
            )


def cert_validexts(cert, policy=[]):
    """valida extensões do certificado.
    'policy' é uma lista de pares '(ext,pred)' onde 'ext' é o OID de uma extensão e 'pred'
    o predicado responsável por verificar o conteúdo dessa extensão."""
    for check in policy:
        ext = cert.extensions.get_extension_for_oid(check[0]).value
        if not check[1](ext):
            raise x509.verification.VerificationError(
                "Certificate extensions does not match expected value"
            )


def valida_certSERVER(ca_cert, crt):
    try:
        # obs: pressupõe que a cadeia de certifica só contém 2 níveis
        crt.verify_directly_issued_by(ca_cert)
        # verificar período de validade...
        cert_validtime(crt)
        # verificar identidade... (e.g.)
        cert_validsubject(crt, [(x509.NameOID.COMMON_NAME, "SSI Message Relay Server")])
        # verificar aplicabilidade... (e.g.)
        # cert_validexts(
        #     cert,
        #     [
        #         (
        #             x509.ExtensionOID.EXTENDED_KEY_USAGE,
        #             lambda e: x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH in e,
        #         )
        #     ],
        # )
        # print("Certificate is valid!")
        return True
    except:
        # print("Certificate is invalid!")
        return False

def valida_certCLIENT(ca_cert, crt):
    try:
        # obs: pressupõe que a cadeia de certifica só contém 2 níveis
        crt.verify_directly_issued_by(ca_cert)
        # verificar período de validade...
        cert_validtime(crt)
        # verificar identidade... (e.g.)
        cert_validsubject(crt, [(x509.NameOID.ORGANIZATIONAL_UNIT_NAME, "SSI MSG RELAY SERVICE")])
        # verificar aplicabilidade... (e.g.)
        # cert_validexts(
        #     cert,
        #     [
        #         (
        #             x509.ExtensionOID.EXTENDED_KEY_USAGE,
        #             lambda e: x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH in e,
        #         )
        #     ],
        # )
        # print("Certificate is valid!")
        return True
    except:
        # print("Certificate is invalid!")
        return False
        

def get_userdata(p12_fname):
    with open(p12_fname, "rb") as f:
        p12 = f.read()
    password = None # p12 não está protegido...
    (private_key, user_cert, [ca_cert]) = pkcs12.load_key_and_certificates(p12, password)
    return (private_key, user_cert, ca_cert)
