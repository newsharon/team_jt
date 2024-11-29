import random
from capture_agents import CaptureAgent
from util import nearest_point


def create_team(first_index, second_index, is_red,
                first='ImprovedCaptureAgent', second='ImprovedCaptureAgent'):
    """
    This function creates a team of two agents.

    Parameters:
    - first_index: Index for the first agent
    - second_index: Index for the second agent
    - is_red: True if the team is red, False otherwise
    - first: The class name of the first agent
    - second: The class name of the second agent
    """
    return [eval(first)(first_index), eval(second)(second_index)]


class MyTeamAgent(CaptureAgent):
    """
    A simple agent that chooses an action randomly.
    """

    def chooseAction(self, gameState):
        """
        Choose the next action to take.

        Parameters:
        - gameState: The current state of the game.

        Returns:
        - A legal action.
        """
        legal_actions = gameState.getLegalActions(self.index)
        chosen_action = random.choice(legal_actions)
        print(f"Agent {self.index} chose action: {chosen_action}")
        return chosen_action


class ImprovedCaptureAgent(CaptureAgent):
    """
    An improved agent that balances food collection, defense, and survival.
    """

    def registerInitialState(self, gameState):
        """
        Called during agent initialization. Use this to set up any state variables.
        """
        super().registerInitialState(gameState)
        self.start = gameState.getAgentPosition(self.index)

    def choose_action(self, gameState):
        """
        Decides the next action for the agent.
        """
        # Get all legal actions
        actions = gameState.get_legal_actions(self.index)

        # Debug: Print available actions
        print(f"Agent {self.index} legal actions: {actions}")

        # Ensure no illegal actions are attempted
        if not actions:
            print(f"Agent {self.index} has no legal actions! Returning 'Stop'.")
            return "Stop"

        # Evaluate actions and choose the best one
        best_action = None
        best_score = float('-inf')

        for action in actions:
            try:
                successor = self.getSuccessor(gameState, action)
                score = self.evaluate(successor, action)
                if score > best_score:
                    best_score = score
                    best_action = action
            except Exception as e:
                # Log details of any illegal actions
                print(f"Agent {self.index} encountered an error with action {action}: {e}")

        # Return the best legal action, or 'Stop' if no valid actions
        if best_action is None:
            print(f"Agent {self.index} could not find a valid action! Returning 'Stop'.")
            return "Stop"

        print(f"Agent {self.index} chose action: {best_action}")
        return best_action

    def getSuccessor(self, gameState, action):
        """
        Finds the successor of the given state after taking an action.
        """
        try:
            successor = gameState.generate_successor(self.index, action)
        except Exception as e:
            print(f"Error generating successor for action {action}: {e}")
            raise e
        return successor

    def evaluate(self, gameState, action):
        """
        Evaluates a game state and assigns a score based on multiple factors.
        """
        successor = self.getSuccessor(gameState, action)
        position = successor.get_agent_position(self.index)
        score = successor.get_score()  # 기본 점수

        # Collect food
        food_list = self.get_food(successor).as_list()
        if food_list:
            closest_food_distance = min([self.get_maze_distance(position, food) for food in food_list])
            score += 10 / (closest_food_distance + 1)  # 가까운 음식 우선

        # Use capsules
        capsules = self.get_capsules(successor)
        if capsules:
            closest_capsule_distance = min([self.get_maze_distance(position, capsule) for capsule in capsules])
            score += 50 / (closest_capsule_distance + 1)  # 캡슐 우선

        # Avoid enemies
        enemies = [successor.get_agent_state(i) for i in self.get_opponents(successor)]
        enemy_positions = [enemy.get_position() for enemy in enemies if enemy.is_pacman is False and enemy.get_position() is not None]
        for enemy_position in enemy_positions:
            distance_to_enemy = self.get_maze_distance(position, enemy_position)
            if distance_to_enemy < 3:  # 가까운 적 회피
                score -= 100 / (distance_to_enemy + 1)

        # Defend against invaders
        if not successor.get_agent_state(self.index).is_pacman:
            invaders = [enemy for enemy in enemies if enemy.is_pacman and enemy.get_position() is not None]
            if invaders:
                closest_invader_distance = min([self.get_maze_distance(position, invader.get_position()) for invader in invaders])
                score -= closest_invader_distance * 2  # 침입자 추적

        return score
