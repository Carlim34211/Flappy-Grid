import pygame
from pygame.locals import K_SPACE
import os
import random

# Constantes
TELA_LARGURA = 700
TELA_ALTURA = 800

IMAGEM_PONTOS = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', '0.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', '1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', '2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', '3.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', '4.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', '5.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', '6.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', '7.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', '8.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', '9.png'))),
]

IMAGEM_GAMEOVER = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'gameover.png')))
IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe-red.png')))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGEM_BACKGROUND = pygame.transform.scale2x(
    pygame.image.load(os.path.join('imgs', '2393204_segathi_flappy-bird-night-background.png'))
)
IMAGENS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bluebird-upflap.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bluebird-midflap.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bluebird-downflap.png'))),
]

# Definir a fonte
pygame.font.init()
FONTE_INSTRUCAO = pygame.font.SysFont('arial', 25)


class Passaro:
    IMGS = IMAGENS_PASSARO
    # Animações da rotação
    ROTACAO_MAXIMA = 10 
    VELOCIDADE_ROTACAO = 15
    TEMPO_ANIMACAO = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0]

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        # Calcular o deslocamento
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo ** 2) + self.velocidade * self.tempo

        # Restringir o deslocamento
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        # O ângulo do passaro
        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):
        # Definir qual imagem do passaro vai usar
        self.contagem_imagem += 1

        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 4:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem >= self.TEMPO_ANIMACAO * 4 + 1:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0

        # Se o passaro tiver caindo eu não vou bater asa
        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO * 2

        # Desenhar a imagem
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)


class Cano:
    DISTANCIA = 200
    VELOCIDADE = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True)
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def mover(self):
        self.x -= self.VELOCIDADE

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if base_ponto or topo_ponto:
            return True
        else:
            return False


class Chao:
    VELOCIDADE = 5
    LARGURA = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))


def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)

    pontos_str = str(pontos)
    largura_pontos = 0
    for digito in pontos_str:
        tela.blit(
            IMAGEM_PONTOS[int(digito)],
            (TELA_LARGURA // 2 - len(pontos_str) * 20 // 2 + largura_pontos, 20),
        )
        largura_pontos += 20

    chao.desenhar(tela)
    pygame.display.update()


def main():
    passaros = [Passaro(230, 350)]
    chao = Chao(730)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontos = 0
    estado_jogo = "executando"  # Inicialize o estado do jogo
    pygame.display.set_caption("CARLIM_GAMEPLAY")
    relogio = pygame.time.Clock()

    rodando = True
    while rodando:
        relogio.tick(30)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    if estado_jogo == "game_over":
                        # Reiniciar o jogo se estiver no estado de Game Over
                        passaros = [Passaro(230, 350)]
                        chao = Chao(730)
                        canos = [Cano(700)]
                        pontos = 0
                        estado_jogo = "executando"

                for passaro in passaros:
                    passaro.pular()

        if estado_jogo == "executando":
            for passaro in passaros:
                passaro.mover()
            chao.mover()

            adicionar_cano = False
            remover_canos = []
            for cano in canos:
                for i, passaro in enumerate(passaros):
                    if cano.colidir(passaro):
                        estado_jogo = "game_over"

                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True
                    pontos += 1

                cano.mover()
                if cano.x + cano.CANO_TOPO.get_width() < 0:
                    remover_canos.append(cano)

            if adicionar_cano:
                canos.append(Cano(600))
            for cano in remover_canos:
                canos.remove(cano)

            for i, passaro in enumerate(passaros):
                if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                    passaros.pop(i)
                    estado_jogo = "game_over"

            desenhar_tela(tela, passaros, canos, chao, pontos)

            # Importante para o resto do jogo
            if estado_jogo == "game_over":
                tela.blit(
                    IMAGEM_GAMEOVER,
                    (TELA_LARGURA // 2 - IMAGEM_GAMEOVER.get_width() // 2, TELA_ALTURA // 3 + 50),
                )
                texto_instrucao = FONTE_INSTRUCAO.render(
                    "Pressione ESPAÇO para reiniciar", 1, (255, 0, 0)
                )
                tela.blit(
                    texto_instrucao,
                    (TELA_LARGURA // 2 - texto_instrucao.get_width() // 2, TELA_ALTURA // 2),
                )
                pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
