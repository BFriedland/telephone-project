Feature: User flow
    Exercises what users see under various circumstances

    Scenario: New user hits home page (root)
        Given A new user
        When I view the home page
        Then I see the first page
        And I can submit a new prompt

    Scenario: Submitting a new prompt on the first page
        When I submit a new prompt "Flibbety Floo"
        Then It is put in the prompts database
        And I see the second page

    # Scenario: Submitting an image on the second page
    #     When I submit a new image on the second page
    #     Then It is put in the prompts database
    #     And I see the third page

    # Scenario: Submitting a new prompt on third page
    #     When I submit a new prompt "Flibbety Floo"
    #     Then It is put in the prompts database
    #     And I see the second page

    # Scenario: Submitting a new prompt on first page
    #     When I submit a new prompt "Flibbety Floo"
    #     Then It is put in the prompts database
    #     And I see the second page

    # Scenario: Submitting a new prompt on first page
    #     When I submit a new prompt "Flibbety Floo"
    #     Then It is put in the prompts database
    #     And I see the second page
