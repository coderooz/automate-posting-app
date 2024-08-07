import requests

class Facebook:
    def __init__(self, access_token):

        """
            Facebook
            ========
            
            This is a class that enables the user to post on personal account or pages programmatically.

        """
        self.access_token = access_token
        self.me = self._requester('https://graph.facebook.com/me', params={'fields': 'id,name,email,gender,birthday,picture'})
        self.pages = {data['name']: {'id': data['id'], 'access_token': data['access_token']} for data in self.get_pages_list()}

    def _requester(self, url: str, method: str = 'get', params: dict = {}, files: dict = {}, new_access_token: str = ''):
        """
        Handles API requests with error handling.
        """
        access_token = new_access_token if new_access_token else self.access_token
        params['access_token'] = access_token
        try:
            if method == 'get':
                response = requests.get(url, params=params)
            elif method == 'post':
                response = requests.post(url, params=params, files=files)
            elif method == 'delete':
                response = requests.delete(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return {'error': str(e)}

    def post_text(self, page_id: str, message: str, link:str=None):
        """
        Posts text to a specified page or personal account.
        
        Parameters:
            page_id (str): The page ID or 'me' for personal account.
            message (str): The message to post.
        
        Returns:
            dict: The API response.
        """
        access_token = self.access_token
        if page_id == 'me':
            page_id = self.me['id']
        elif page_id in self.pages:
            access_token = self.pages[page_id]['access_token']
            page_id = self.pages[page_id]['id']
        else:
            # Attempt to find the page if it's an ID that needs to be resolved
            page_info = self.select_page(page_id)
            if page_info:
                page_id = page_info['id']
                access_token = page_info['access_token']
            else:
                print(f"Page '{page_id}' not found.")
                return {'error': 'Page ID or user account not found'}

        return self._requester(f'https://graph.facebook.com/{page_id}/feed', 'post', params={'message': message, 'link': link}, new_access_token=access_token)

    def post_text_with_images(self, page_id: str, message: str, photos: list):
        """
        Posts text with multiple images to a specified page.
        
        Parameters:
            page_id (str): The page ID where the content will be posted.
            message (str): The message to post.
            photos (list): List of paths to photo files to upload.
        
        Returns:
            dict: The API response.
        """
        responses = []
        for photo_path in photos:
            with open(photo_path, 'rb') as photo_file:
                files = {'source': photo_file}
                response = self._requester(f'https://graph.facebook.com/{page_id}/photos', 'post', params={'caption': message}, files=files)
                responses.append(response)
        return {'photos': responses}

    def post_text_with_video(self, page_id: str, message: str, video_path: str):
        """
        Posts text with a video to a specified page.
        
        Parameters:
            page_id (str): The page ID where the content will be posted.
            message (str): The message to post.
            video_path (str): The path to the video file to upload.
        
        Returns:
            dict: The API response.
        """
        with open(video_path, 'rb') as video_file:
            files = {'source': video_file}
            return self._requester(f'https://graph.facebook.com/{page_id}/videos', 'post', params={'description': message}, files=files)

    def post_bulk(self, page_id: str, contents: list):
        """
        Posts multiple messages or content to a specified page.
        
        Parameters:
            page_id (str): The page ID where the content will be posted.
            contents (list): List of dictionaries with content to post. Each dictionary can contain 'message', 'link', 'photos', 'videos'.
        
        Returns:
            list: List of API responses for each post.
        """
        responses = []
        for content in contents:
            if 'photos' in content:
                response = self.post_text_with_images(
                    page_id,
                    message=content.get('message', ''),
                    photos=content.get('photos', [])
                )
            elif 'videos' in content:
                response = self.post_text_with_video(
                    page_id,
                    message=content.get('message', ''),
                    video_path=content.get('videos', [])[0]  # Assumes one video per post
                )
            else:
                response = self._requester(f'https://graph.facebook.com/{page_id}/feed', 'post', params={
                    'message': content.get('message', ''),
                    'link': content.get('link')
                })
            responses.append(response)
        return responses

    def get_posts_list(self, page_name: str, limit: int = 10) -> list:
        """
        Retrieves a list of posts from a specified page or user feed.
        
        Parameters:
            page_name (str): The name of the page or 'me' for user posts.
            limit (int): The number of posts to retrieve. Defaults to 10.
        
        Returns:
            list: A list of posts.
        """
        page_id = ''
        access_token = ''
        if page_name in self.pages:
            page_id = self.pages[page_name]['id']
            access_token = self.pages[page_name]['access_token']
        elif page_name == 'me':
            page_id = self.me['id']
            access_token = self.access_token
        else:
            page_id = self.select_page(page_name)
            access_token = self.pages.get(page_name, {}).get('access_token', '')

        if not page_id or not access_token:
            print(f"Page '{page_name}' not found.")
            return []

        posts = self._requester(f'https://graph.facebook.com/{page_id}/posts', params={'limit': limit}, new_access_token=access_token)
        if 'error' in posts:
            print(f"Error fetching posts: {posts['error']}")
            return []
        return posts.get('data', [])

    def get_pages_list(self) -> list:
        """
        Fetches the list of pages that the user has access to.
        
        Returns:
            list: A list of pages.
        """
        response = self._requester('https://graph.facebook.com/me/accounts')
        if 'error' in response:
            print(f"Error fetching pages: {response['error']}")
            return []
        return response.get('data', [])

    def edit_post(self, post_id: str, message: str, page_name:str):
        """
        Edits an existing post on a page or personal account.
        
        Parameters:
            post_id (str): The ID of the post to edit.
            message (str): The new message content.
        
        Returns:
            dict: The API response.
        """
        if page_name in self.pages:
            access_token = self.pages[page_name]['access_token']
        elif page_name=='me':
            access_token = self.access_token
        else:
            print(f'Page {page_name} not found.')
            return {}
        
        response = self._requester(f'https://graph.facebook.com/{post_id}', 'post', params={'message': message}, new_access_token=access_token)
        if 'error' in response:
            print(f"Error editing post: {response['error']}")
        return response

    def delete_post(self, post_id: str, page_name:str):
        """
        Edits an existing post on a page or personal account.
        
        Parameters:
            post_id (str): The ID of the post to edit.
            message (str): The new message content.
        
        Returns:
            dict: The API response.
        """
        if page_name in self.pages:
            access_token = self.pages[page_name]['access_token']
        elif page_name=='me':
            access_token = self.access_token
        else:
            print(f'Page {page_name} not found.')
            return {}
        
        response = self._requester(f'https://graph.facebook.com/{post_id}', 'delete', new_access_token=access_token)
        if 'error' in response:
            print(f"Error editing post: {response['error']}")
        return response


    def select_page(self, page_name: str) -> dict:
        """
        Selects a page based on the page name.
        
        Parameters:
            page_name (str): The name of the page to select.
        
        Returns:
            dict: The page information including ID and access token, if found.
        """
        pages = self.get_pages_list()
        for page in pages:
            if page['name'] == page_name:
                return {'id': page['id'], 'access_token': page['access_token']}
        print(f"Page '{page_name}' not found.")
        return {}
    
