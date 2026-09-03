from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9175764a1cd5'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('usuario',
    sa.Column('nome', sa.String(length=160), nullable=False),
    sa.Column('email', sa.String(length=160), nullable=False),
    sa.Column('senha_hash', sa.String(length=255), nullable=False),
    sa.Column('papel', sa.Enum('advogado', 'administrador', name='papelusuario', native_enum=False, length=32), nullable=False),
    sa.Column('oab', sa.String(length=40), nullable=True),
    sa.Column('ativo', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('usuario', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_usuario_email'), ['email'], unique=True)

    op.create_table('processo',
    sa.Column('numero_processo', sa.String(length=40), nullable=True),
    sa.Column('status', sa.Enum('bloqueado', 'aberto', 'concluido', name='statusprocesso', native_enum=False, length=32), nullable=False),
    sa.Column('data_abertura', sa.Date(), nullable=True),
    sa.Column('data_obito', sa.Date(), nullable=True),
    sa.Column('nome_de_cujus', sa.String(length=200), nullable=False),
    sa.Column('cpf_de_cujus', sa.String(length=14), nullable=False),
    sa.Column('ultimo_domicilio', sa.String(length=200), nullable=True),
    sa.Column('regime_bens', sa.String(length=80), nullable=True),
    sa.Column('responsavel_id', sa.Uuid(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['responsavel_id'], ['usuario.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('processo', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_processo_numero_processo'), ['numero_processo'], unique=False)
        batch_op.create_index(batch_op.f('ix_processo_responsavel_id'), ['responsavel_id'], unique=False)

    op.create_table('bem',
    sa.Column('processo_id', sa.Uuid(), nullable=False),
    sa.Column('descricao', sa.String(length=300), nullable=False),
    sa.Column('categoria', sa.Enum('imovel', 'imovel_rural', 'movel', 'financeiro', 'outro', name='categoriabem', native_enum=False, length=32), nullable=False),
    sa.Column('valor_estimado', sa.Numeric(precision=16, scale=2), nullable=False),
    sa.Column('identificador', sa.String(length=120), nullable=True),
    sa.Column('origem', sa.Enum('formulario', 'documento', name='origembem', native_enum=False, length=32), nullable=False),
    sa.Column('status', sa.Enum('nao_iniciado', 'pendente', 'em_analise', 'concluido', 'rejeitado', name='statusitem', native_enum=False, length=32), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['processo_id'], ['processo.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('bem', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_bem_processo_id'), ['processo_id'], unique=False)

    op.create_table('documento',
    sa.Column('processo_id', sa.Uuid(), nullable=False),
    sa.Column('tipo', sa.Enum('certidao_obito', 'cnd_federal', 'cnd_estadual', 'cnd_municipal', 'certidao_censec', 'certidao_matricula', 'certidao_casamento', 'certidao_nascimento', 'documento_identidade', 'extrato_bancario', 'documento_veiculo', 'declaracao_irpf', 'outro', name='tipodocumento', native_enum=False, length=40), nullable=False),
    sa.Column('tipo_detectado', sa.Enum('certidao_obito', 'cnd_federal', 'cnd_estadual', 'cnd_municipal', 'certidao_censec', 'certidao_matricula', 'certidao_casamento', 'certidao_nascimento', 'documento_identidade', 'extrato_bancario', 'documento_veiculo', 'declaracao_irpf', 'outro', name='tipodocumento', native_enum=False, length=40), nullable=True),
    sa.Column('nome_arquivo', sa.String(length=255), nullable=False),
    sa.Column('caminho_arquivo', sa.String(length=500), nullable=True),
    sa.Column('tamanho_bytes', sa.Integer(), nullable=False),
    sa.Column('status_validacao', sa.Enum('nao_iniciado', 'pendente', 'em_analise', 'concluido', 'rejeitado', name='statusitem', native_enum=False, length=32), nullable=False),
    sa.Column('motivo_status', sa.Text(), nullable=True),
    sa.Column('texto_extraido', sa.Text(), nullable=True),
    sa.Column('metodo_extracao', sa.String(length=20), nullable=True),
    sa.Column('origem', sa.Enum('upload_manual', 'busca_automatica', name='origemdocumento', native_enum=False, length=32), nullable=False),
    sa.Column('recebido_em', sa.DateTime(timezone=True), nullable=False),
    sa.Column('processamento_iniciado_em', sa.DateTime(timezone=True), nullable=True),
    sa.Column('processamento_concluido_em', sa.DateTime(timezone=True), nullable=True),
    sa.Column('erro_processamento', sa.Text(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['processo_id'], ['processo.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('documento', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_documento_processo_id'), ['processo_id'], unique=False)

    op.create_table('evento',
    sa.Column('processo_id', sa.Uuid(), nullable=False),
    sa.Column('tipo', sa.Enum('processo_criado', 'processo_desbloqueado', 'documento_recebido', 'documento_validado', 'documento_rejeitado', 'documento_erro', 'herdeiro_cadastrado', 'bem_declarado', 'inconsistencia_detectada', 'pendencia_resolvida', name='tipoevento', native_enum=False, length=40), nullable=False),
    sa.Column('descricao', sa.Text(), nullable=False),
    sa.Column('status', sa.Enum('nao_iniciado', 'pendente', 'em_analise', 'concluido', 'rejeitado', name='statusitem', native_enum=False, length=32), nullable=False),
    sa.Column('referencia_id', sa.Uuid(), nullable=True),
    sa.Column('ator', sa.String(length=160), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['processo_id'], ['processo.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('evento', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_evento_processo_id'), ['processo_id'], unique=False)

    op.create_table('herdeiro',
    sa.Column('processo_id', sa.Uuid(), nullable=False),
    sa.Column('nome', sa.String(length=200), nullable=False),
    sa.Column('cpf', sa.String(length=14), nullable=True),
    sa.Column('parentesco', sa.String(length=60), nullable=False),
    sa.Column('pre_morto', sa.Boolean(), nullable=False),
    sa.Column('conjuge', sa.Boolean(), nullable=False),
    sa.Column('representa_herdeiro_id', sa.Uuid(), nullable=True),
    sa.Column('status', sa.Enum('nao_iniciado', 'pendente', 'em_analise', 'concluido', 'rejeitado', name='statusitem', native_enum=False, length=32), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['processo_id'], ['processo.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['representa_herdeiro_id'], ['herdeiro.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('herdeiro', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_herdeiro_processo_id'), ['processo_id'], unique=False)

    op.create_table('entidade_extraida',
    sa.Column('documento_id', sa.Uuid(), nullable=False),
    sa.Column('categoria', sa.Enum('pessoa', 'data', 'local', 'patrimonio', 'fiscal', 'registro', 'outro', name='categoriaentidade', native_enum=False, length=32), nullable=False),
    sa.Column('chave', sa.String(length=80), nullable=False),
    sa.Column('valor', sa.Text(), nullable=False),
    sa.Column('confianca', sa.Float(), nullable=False),
    sa.Column('modelo_llm', sa.String(length=80), nullable=False),
    sa.Column('versao_extracao', sa.Integer(), nullable=False),
    sa.Column('duracao_ms', sa.Integer(), nullable=True),
    sa.Column('extraido_em', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['documento_id'], ['documento.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('entidade_extraida', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_entidade_extraida_documento_id'), ['documento_id'], unique=False)

    op.create_table('pendencia',
    sa.Column('processo_id', sa.Uuid(), nullable=False),
    sa.Column('categoria', sa.Enum('documento_ausente', 'documento_invalido', 'inconsistencia', name='categoriapendencia', native_enum=False, length=32), nullable=False),
    sa.Column('tipo_documento', sa.Enum('certidao_obito', 'cnd_federal', 'cnd_estadual', 'cnd_municipal', 'certidao_censec', 'certidao_matricula', 'certidao_casamento', 'certidao_nascimento', 'documento_identidade', 'extrato_bancario', 'documento_veiculo', 'declaracao_irpf', 'outro', name='tipodocumento', native_enum=False, length=40), nullable=True),
    sa.Column('documento_id', sa.Uuid(), nullable=True),
    sa.Column('titulo', sa.String(length=200), nullable=False),
    sa.Column('descricao', sa.Text(), nullable=True),
    sa.Column('bloqueante', sa.Boolean(), nullable=False),
    sa.Column('link_portal', sa.String(length=500), nullable=True),
    sa.Column('resolvida', sa.Boolean(), nullable=False),
    sa.Column('resolvida_em', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['documento_id'], ['documento.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['processo_id'], ['processo.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('pendencia', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_pendencia_processo_id'), ['processo_id'], unique=False)



def downgrade() -> None:
    with op.batch_alter_table('pendencia', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_pendencia_processo_id'))

    op.drop_table('pendencia')
    with op.batch_alter_table('entidade_extraida', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_entidade_extraida_documento_id'))

    op.drop_table('entidade_extraida')
    with op.batch_alter_table('herdeiro', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_herdeiro_processo_id'))

    op.drop_table('herdeiro')
    with op.batch_alter_table('evento', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_evento_processo_id'))

    op.drop_table('evento')
    with op.batch_alter_table('documento', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_documento_processo_id'))

    op.drop_table('documento')
    with op.batch_alter_table('bem', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_bem_processo_id'))

    op.drop_table('bem')
    with op.batch_alter_table('processo', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_processo_responsavel_id'))
        batch_op.drop_index(batch_op.f('ix_processo_numero_processo'))

    op.drop_table('processo')
    with op.batch_alter_table('usuario', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_usuario_email'))

    op.drop_table('usuario')
