Feature: User flow
    Exercises what users see under various circumstances

    Scenario: New user hits home page (root)
        Given A new user
        When I view the home page
        Then I see the first page
        And I can submit a new prompt

    # Scenario: Logged in user can see add entry form
    #     Given an authenticated user
    #     When I view the home page
    #     Then I do see the new entry form

    # Scenario: Anonymous user cannot submit add form
    #     Given an anonymous user
    #     And the title "New Post"
    #     And the text "This is a new post"
    #     When I submit the add form
    #     Then I am redirected to the home page
    #     And I do not see my new entry

    # Scenario: Logged in user can submit add form
    #     Given an authenticated user
    #     And the title "New Post"
    #     And the text "This is a new post"
    #     When I submit the add form
    #     Then I am redirected to the home page
    #     And I see my new entry
