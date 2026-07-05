import pygame

from hud import CYAN, TEXT, TEXT_DIM


def show_welcome_screen(engine):
    clock = pygame.time.Clock()

    while True:
        engine.screen.fill((4, 7, 10))

        title = engine.font_big.render(
            "CREA-J",
            True,
            CYAN
        )

        subtitle = engine.font_med.render(
            "Sistema inteligente de monitoreo",
            True,
            TEXT
        )

        message = engine.font_med.render(
            "Presiona ENTER para continuar",
            True,
            TEXT_DIM
        )

        title_rect = title.get_rect(
            center=(engine.width // 2, engine.height // 2 - 80)
        )

        subtitle_rect = subtitle.get_rect(
            center=(engine.width // 2, engine.height // 2)
        )

        message_rect = message.get_rect(
            center=(engine.width // 2, engine.height // 2 + 100)
        )

        engine.screen.blit(title, title_rect)
        engine.screen.blit(subtitle, subtitle_rect)
        engine.screen.blit(message, message_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    engine.voice.say_async(
                        "Bienvenido al sistema de monitoreo de NeuroSpace."
                    )
                    return

        clock.tick(60)