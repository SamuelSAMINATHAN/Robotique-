from robomaster import robot

def main():
    """
    Lit un fichier audio sur le robot RoboMaster.
    - robot_ip : adresse IP du robot.
    - local_audio_file : fichier audio local à lire.
    """
    robot_ip = "192.168.2.1"
    local_audio_file = "sucess_en.wav"  # Remplacez par le nom de votre fichier audio
    remote_audio_file = local_audio_file 

    try:
        print("\nInitialisation du robot via le SDK...")
        ep_robot = robot.Robot()
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
