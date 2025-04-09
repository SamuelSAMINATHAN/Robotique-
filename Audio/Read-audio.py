from robomaster import robot

def main():
    # Paramètres de base
    robot_ip = "192.168.2.1"  # Adaptez si nécessaire
    local_audio_file = "a.wav"
    remote_audio_file = local_audio_file 

    # 2. Lecture du fichier via le SDK
    try:
        print("\nInitialisation du robot via le SDK...")
        ep_robot = robot.Robot()
        # Pas de paramètre IP, on s'appuie sur la config par défaut (mode STA)
        ep_robot.initialize()
        print("Connexion SDK réussie.")

        print(f"Lecture du fichier audio '{remote_audio_file}'...")
        ep_robot.play_audio(filename=remote_audio_file).wait_for_completed()
        print("Lecture terminée.")

        ep_robot.close()
    except Exception as e:
        print("Erreur lors de la lecture audio via le SDK :", e)

if __name__ == '__main__':
    main()
