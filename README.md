<h1> Draft - Embracing spontaneity in travel. </h1>

View the companion iOS app here: https://github.com/ZainKho/draft

*Let your vacation muse take you away*: Draft lets you plan out trips and vacations, and share them with friends and family.

View designs here: https://www.figma.com/file/LrYb6NKKZ9A6VnmZbJ8AJx/Draft?node-id=0%3A1

### Hack Challenge

This project (iOS app, Backend) was developed as part of the Hack Challenge. Cornell AppDev offers four courses in iOS Development, Backend Development, Digital Product Design, and (soon) Android Development. Check it out here:
- Cornell AppDev: https://www.cornellappdev.com/
- Hack Challenge: https://www.cornellappdev.com/hack-challenge

### Information pertinent to backenders

I have set up an instance of the backend running at: https://draft-backend.duckdns.org/. Come check it out!

Draft uses the Unsplash API to pull images for the frontend. It works (as far as I know) without an API key so no worries there. 
However, if you would like to use Draft to its fullest, enable Unsplash images by adding `UNSPLASH_ACCESS_KEY` to your environment.

There exists a branch `william/authentication` that is a full implementation of user login and authentication that is currently unused :(


### Information pertinent to frontenders

#### Get all users: ```GET /api/users/```
Response:
```
{
    "success": true,
    "data": [
        {
            "id": 1,
            "name": "Zainkho",
            "trips": [
                {
                    "id": 1,
                    "location": "Paris",
                    "name": "Never Gonna Graduate!",
                    "start": 10000,
                    "entries": [
                        {
                            "id": 5,
                            "description": "Visit the tunnel between Uris and Olin",
                            "kind": "attraction",
                            "completed": false,
                            "day_index": 3
                        },
                        {
                            "id": 6,
                            "description": "Sing At Cornell",
                            "kind": "resturant",
                            "completed": false,
                            "day_index": 3
                        }
                    ],
                    "image_url": "...",
                    "image_credit": "Paul Dufour"
                },
                ...
            ]
        }
    ]
}
```

```image_url``` is the unsplash image. ```image_credit``` is the attribution. Both these parameters may or may not be returned.

#### Get Specific User: `GET /api/user/<user_id>/`
Response:
```
{
    "success": true,
    "data": {
        "id": 1,
        "name": "Zainkho",
        "trips": [
            {
                "id": 1,
                "location": "Paris",
                "name": "Never Gonna Graduate!",
                "start": 10000,
                "entries": [
                    {
                        "id": 5,
                        "description": "Visit the tunnel between Uris and Olin",
                        "kind": "attraction",
                        "completed": false,
                        "day_index": 3
                    },
                    {
                        "id": 6,
                        "description": "Sing At Cornell",
                        "kind": "resturant",
                        "completed": false,
                        "day_index": 3
                    }
                ],
                "image_url": "...",
                "image_credit": "Paul Dufour"
            },
            ...
        ]
    }
}
```

#### Create New User: `POST /api/users/`
Post Body:
```
{
	"name": "Zainkho"
}
```
Response:
```
{
    "success": true,
    "data": {
        "id": 1,
        "name": "Zainkho",
        "trips": []
    }
}
```
If you want to retrieve the same user again, save the user id here.

#### Create A New Trip: `POST /api/user/<user_id>/trip/`
Post Body:
```
{
	"name": "Senior Trip 2023",
  "start": 10000, // optional
	"location": "Paris", // optional, won't get any unsplash images if not included
	"entries": [
		{
			"description": "Streaking across Schlokelpt Field",
			"kind": "resturant",
			"day_index": 5
		},
		{
			"description": "Attempt to box Michael George",
			"kind": "attraction",
			"day_index": 4
		}
	]
}
```
Response:
```
{
    "success": true,
    "data": {
        "id": 2,
        "location": "Paris",
        "name": "Senior Trip 2023",
        "start": 10000,
        "entries": [
            {
                "id": 3,
                "description": "Streaking across Schlokelpt Field",
                "kind": "resturant",
                "completed": false,
                "day_index": 5
            },
            {
                "id": 4,
                "description": "Attempt to box Michael George",
                "kind": "attraction",
                "completed": false,
                "day_index": 4
            }
        ],
        "image_url": "...",
        "image_credit": "Chris Karidis"
    }
}
```

#### Update A Trip: `PUT /api/trip/<trip_id>/`
Put Body:
```
{
	"name": "Never Gonna Graduate!",
	"start": 10000,
	"entries": [
		{
			"description": "Visit the tunnel between Uris and Olin",
			"kind": "attraction",
			"day_index": 3
		},
		{
			"description": "Sing At Cornell",
			"kind": "resturant",
			"day_index": 3
		}
	]
}
```
Response:
```
{
    "success": true,
    "data": {
        "id": 1,
        "location": "Paris",
        "name": "Never Gonna Graduate!",
        "start": 10000,
        "entries": [
            {
                "id": 5,
                "description": "Visit the tunnel between Uris and Olin",
                "kind": "attraction",
                "completed": false,
                "day_index": 3
            },
            {
                "id": 6,
                "description": "Sing At Cornell",
                "kind": "resturant",
                "completed": false,
                "day_index": 3
            }
        ],
        "image_url": "...",
        "image_credit": "Paul Dufour"
    }
}
```
