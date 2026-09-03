class ErroServico(Exception):
    status_http = 400


class NaoEncontrado(ErroServico):
    status_http = 404


class AcessoNegado(ErroServico):
    status_http = 403


class RegraDeNegocio(ErroServico):
    status_http = 422
