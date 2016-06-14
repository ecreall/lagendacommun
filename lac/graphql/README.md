To build schema.json (needed if you use relay js lib):

    mkvirtualenv -p python3 graphene
    pip install graphene
    python schema.py


Example:

    query MyQuery ($after: String) {
      events: culturalEvents(
          first: 30,
          after: $after,
          text: "",
          dates: ["2016-05-21", "2016-06-02", "2016-07-23"],
          categories: ["Théâtre", "Loisirs"],
          cities: ["France@59650"]) {
        pageInfo{
          endCursor,
          hasNextPage,
        },
        edges{
          node{
            url,
            calendar,
            title,
            description,
            picture(size: "small"),
            artists(first: 2){
              pageInfo{
                endCursor,
                hasNextPage,
              },
              edges{
                node{
                  title
                }
              }
            },
            contacts {
              edges{
                node{
                  website,
                  email,
                  phone,
                  surtax,
                  fax
                }
              }
            },
            schedules {
              edges{
                node{
                  datesStr,
                  calendar,
                  venue {
                    edges{ 
                      node{
                        title,
                        address {
                          edges{
                            node{
                              country,
                              city,
                              zipcode,
                              department,
                              address,
                              addressStr,
                              geoLocation # lat,long
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }

Query variables :

    {"after": ""}

After the user login:

    { 
      user: currentUser {
        edges {
           node {
            email,
            myEvents {
              edges {
                node {
                  title,
                  state
                }
              }
            }
          }
        }
      }
    }


Login:

    POST: $.post(
          "host/creationculturelapi",
          {op:"login", password: "thepassword", login:"email"}, function(data){})

    URL: "host/creationculturelapi?op=login&password=thepassword&login=email"

Login with FB:

    POST: $.post(
          "host/creationculturelapi",
          {op:"login", external_login: true, user_name="username", userid="userid", domain="domain"...}, function(data){})

Logout:

    POST: $.post(
          "host/creationculturelapi",
          {op:"logout"}, function(data){})

    URL: "host/creationculturelapi?op=logout"
