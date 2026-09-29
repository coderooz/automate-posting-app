import requests


class Instagram:
    def __init__(self, access_token, business_account_id):
        """
        Initialize the Instagram API client.

        Parameters:
            access_token (str): Access token for Instagram Graph API.
            business_account_id (str): The Instagram Business Account ID.
        """
        self.access_token = access_token
        self.business_account_id = business_account_id
        self.base_url = 'https://graph.facebook.com/v14.0'

    def _requester(self, endpoint: str, method: str = 'get', params: dict = {}, files: dict = {}):
        """
        Handles API requests with error handling.

        Parameters:
            endpoint (str): API endpoint.
            method (str): HTTP method ('get', 'post', etc.).
            params (dict): Query parameters.
            files (dict): Files to upload.

        Returns:
            dict: The API response.
        """
        params['access_token'] = self.access_token
        url = f"{self.base_url}/{endpoint}"
        try:
            if method == 'get':
                response = requests.get(url, params=params)
            elif method == 'post':
                response = requests.post(url, params=params, files=files)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return {'error': str(e)}

    def post_text(self, caption: str, image_url: str):
        """
        Posts a text and image to Instagram.

        Parameters:
            caption (str): The caption for the post.
            image_url (str): URL of the image to post.

        Returns:
            dict: The API response.
        """
        # Step 1: Create a container
        container_params = {
            'image_url': image_url,
            'caption': caption,
        }
        container_response = self._requester(
            f'{self.business_account_id}/media',
            'post',
            params=container_params
        )
        if 'error' in container_response:
            return container_response

        # Step 2: Publish the container
        creation_id = container_response.get('id')
        publish_response = self._requester(
            f'{self.business_account_id}/media_publish',
            'post',
            params={'creation_id': creation_id}
        )
        return publish_response

    def get_recent_media(self, limit: int = 10):
        """
        Retrieves recent media from the Instagram Business Account.

        Parameters:
            limit (int): The number of media items to retrieve. Defaults to 10.

        Returns:
            list: A list of media items.
        """
        media_response = self._requester(
            f'{self.business_account_id}/media',
            'get',
            params={'fields': 'id,caption,media_type,media_url,thumbnail_url,permalink', 'limit': limit}
        )
        if 'error' in media_response:
            print(f"Error fetching media: {media_response['error']}")
            return []
        return media_response.get('data', [])

    def get_media_details(self, media_id: str):
        """
        Retrieves details of a specific media item.

        Parameters:
            media_id (str): The ID of the media item.

        Returns:
            dict: The media details.
        """
        media_response = self._requester(
            f'{media_id}',
            'get',
            params={'fields': 'id,caption,media_type,media_url,thumbnail_url,permalink'}
        )
        if 'error' in media_response:
            print(f"Error fetching media details: {media_response['error']}")
        return media_response
